#!/usr/bin/env python3
# designer: I install the personal-knowledge layer (inbox, logs, note
#   templates, index) in your project without overwriting anything you
#   already wrote. I tell you which files I created and which I skipped, and
#   I never edit your CLAUDE.md: I only suggest the line to add.
"""
pkb_inbox.py -- PKB layer tooling (init, capture).

Invocation: agent-invoked, user-invoked via /seja-setup --pkb
Lifecycle: active

Usage:
    pkb_inbox.py init [--target DIR] [--with-skills] [--dry-run] [--json]
    pkb_inbox.py capture --skill NAME --artifact PATH_OR_ID --session-id ID
                         [--brief TEXT] [--target DIR] [--json]

Exit codes: 0 ok, 1 error, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "design"))
from check_secrets import SECRET_PATTERNS
from conversation_trace import list_entries

SCHEMA_VERSION = 1
DEFAULT_PKB_DIR = "inbox"
TEMPLATE_ROOT = Path(__file__).resolve().parent.parent.parent / "references" / "template" / "pkb"
_PKB_ROW = re.compile(r"^\|\s*`PKB_DIR`\s*\|\s*`?([^`|]*?)`?\s*\|", re.MULTILINE)


def read_pkb_dir(target: Path) -> str:
    """Return PKB_DIR from the target's conventions.md, default 'inbox'."""
    conv = target / "product-design" / "conventions.md"
    if conv.is_file():
        match = _PKB_ROW.search(conv.read_text(encoding="utf-8"))
        if match and match.group(1).strip():
            return match.group(1).strip().strip("/")
    return DEFAULT_PKB_DIR


def _conv_row(target: Path, key: str) -> str | None:
    """Raw value of a conventions.md table row, or None when the row is absent."""
    conv = target / "product-design" / "conventions.md"
    if not conv.is_file():
        return None
    match = re.search(
        rf"^\|\s*`{re.escape(key)}`\s*\|\s*`?([^`|]*?)`?\s*\|",
        conv.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1).strip() if match else None


def pkb_layer_present(repo_root: Path) -> bool:
    """True when PKB_DIR is non-empty and <PKB_DIR>/README.md exists.

    An empty PKB_DIR row turns the layer off; an absent row means the default.
    """
    raw = _conv_row(repo_root, "PKB_DIR")
    pkb_dir = DEFAULT_PKB_DIR if raw is None else raw.strip("/")
    return bool(pkb_dir) and (repo_root / pkb_dir / "README.md").is_file()


def _trace_file(repo_root: Path) -> Path:
    raw = _conv_row(repo_root, "CONVERSATION_TRACE_FILE")
    out = _conv_row(repo_root, "OUTPUT_DIR") or "_output"
    if not raw:
        raw = "${OUTPUT_DIR}/conversation-trace.jsonl"
    return repo_root / raw.replace("${OUTPUT_DIR}", out.strip("/"))


def _mask(text: str) -> tuple[str, bool]:
    masked = text
    for name, pattern in SECRET_PATTERNS:
        masked = pattern.sub(f"[MASKED:{name}]", masked)
    return masked, masked != text


def _normalize(text: str) -> str:
    """casefold, drop blockquote markers, collapse spaces, strip edge quotes/punctuation."""
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
    text = " ".join(text.casefold().split())
    return text.strip(" \t\"'\u201c\u201d.,;:!?")


def _plan_brief(artifact: Path) -> str | None:
    if not artifact.is_file():
        return None
    match = re.search(r"^## User brief\s*\n(.*?)(?=^## |\Z)",
                      artifact.read_text(encoding="utf-8"), re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


def _artifact_id(artifact: str) -> str:
    stem = Path(artifact).stem
    match = re.match(r"^([a-z]+-(?:\d{6}|\d{8}-[0-9a-z]{6}))", stem)
    return match.group(1) if match else stem


def _slug(text: str) -> str:
    words = re.findall(r"[a-z0-9]+", text.casefold().encode("ascii", "ignore").decode())
    return "-".join(words[:5]) or "captura"


def capture(skill: str, artifact: str, session_id: str, brief: str | None,
            repo_root: Path) -> dict:
    """Write (or extend) the inbox note derived from trace + brief."""
    if not pkb_layer_present(repo_root):
        return {"skipped": "no-pkb-layer"}
    skill_id = skill.lstrip("/")
    entries = [
        e for e in list_entries(session_id, trace_file=_trace_file(repo_root))
        if e.get("emitter") == "user"
        and (e.get("led_to_skill") or "").lstrip("/") == skill_id
    ]
    quotes: list[tuple[str, str]] = []  # (HH:MM, text)
    for e in entries:
        stamp = str(e.get("timestamp", ""))
        try:
            hhmm = datetime.fromisoformat(stamp).strftime("%H:%M")
        except ValueError:
            hhmm = "--:--"
        quotes.append((hhmm, str(e.get("message", ""))))
    fonte: list[str] | str = [str(e["evt_id"]) for e in entries]
    if not quotes:
        if not brief:
            return {"skipped": "nothing-to-capture"}
        fonte = "briefs"
        quotes = [("--:--", brief)]
    texts = [_mask(t) for _, t in quotes]
    mascarado = any(flag for _, flag in texts)
    body_lines = [f"> **{hhmm}** {t.replace(chr(10), chr(10) + '> ')}"
                  for (hhmm, _), (t, _) in zip(quotes, texts)]
    gathered = " ".join(t for t, _ in texts)
    if fonte != "briefs" and brief:
        brief_masked, brief_flag = _mask(brief)
        mascarado = mascarado or brief_flag
        body_lines.append(f"> **brief** {brief_masked}")

    art_path = Path(artifact)
    if not art_path.is_absolute():
        art_path = repo_root / art_path
    igual = None
    plan_brief = _plan_brief(art_path)
    if plan_brief is not None:
        igual = _normalize(gathered) == _normalize(plan_brief)
    try:
        artefato = art_path.relative_to(repo_root).as_posix()
    except ValueError:
        artefato = artifact

    today = datetime.now(timezone.utc).date().isoformat()
    pkb_dir = repo_root / (_conv_row(repo_root, "PKB_DIR") or DEFAULT_PKB_DIR).strip("/")
    safe_skill = re.sub(r"[^a-z0-9]+", "-", skill_id.split()[0].casefold()).strip("-") or "skill"
    name = f"{today}-{safe_skill}-{_artifact_id(artifact)}-{_slug(gathered)}.md"
    note = pkb_dir / name
    body = "\n".join(body_lines) + "\n"
    if note.exists():
        with note.open("a", encoding="utf-8", newline="") as f:
            f.write(f"\n## Acrescentado em {today}\n\n{body}")
    else:
        fonte_yaml = fonte if isinstance(fonte, str) else "[" + ", ".join(fonte) + "]"
        front = [
            "---", "origem: usuario", "tipo: transitoria", f"tags: [seja, {safe_skill}]",
            f"data: {today}", f"skill: {skill_id}", f"artefato: {artefato}",
            f"fonte: {fonte_yaml}", f"mascarado: {str(mascarado).lower()}",
        ]
        if igual is not None:
            front.append(f"as_expressed_igual_ao_brief: {str(igual).lower()}")
        front.append("---")
        note.write_text("\n".join(front) + f"\n\n{body}", encoding="utf-8", newline="")
    return {"schema_version": SCHEMA_VERSION, "path": note.relative_to(repo_root).as_posix(),
            "fonte": fonte, "mascarado": mascarado, "as_expressed_igual_ao_brief": igual}


def _cmd_capture(args: argparse.Namespace) -> int:
    root = Path(args.target).resolve() if args.target else Path.cwd()
    result = capture(args.skill, args.artifact, args.session_id, args.brief, root)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif "skipped" in result:
        print(f"skipped: {result['skipped']}")
    else:
        print(f"captured {result['path']}")
        if result["mascarado"]:
            print("WARNING: secret-like text was masked in the note", file=sys.stderr)
    return 0


def _plan(target: Path, template_root: Path, with_skills: bool) -> list[tuple[Path | None, Path]]:
    """List (source, destination) pairs; source None means an empty placeholder."""
    pkb_dir = read_pkb_dir(target)
    pairs: list[tuple[Path | None, Path]] = []
    for src in sorted(template_root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(template_root)
        if rel.parts[0] == "skills":
            if with_skills:
                pairs.append((src, target / ".claude" / "skills" / Path(*rel.parts[1:])))
            continue
        if rel.parts[0] == "inbox":
            rel = Path(pkb_dir, *rel.parts[1:])
        pairs.append((src, target / rel))
    pairs.append((None, target / pkb_dir / ".gitkeep"))
    pairs.append((None, target / "logs" / str(datetime.now(timezone.utc).year) / ".gitkeep"))
    return pairs


def init_layer(target: Path, template_root: Path, with_skills: bool, dry_run: bool) -> dict:
    """Copy the PKB template into target without overwriting existing files."""
    created: list[str] = []
    skipped: list[str] = []
    for src, dest in _plan(target, template_root, with_skills):
        rel = dest.relative_to(target).as_posix()
        if dest.exists():
            skipped.append(rel)
            continue
        created.append(rel)
        if dry_run:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src is None:
            dest.write_bytes(b"")
        else:
            dest.write_bytes(src.read_bytes())
    return {"schema_version": SCHEMA_VERSION, "created": created, "skipped": skipped}


def _cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve() if args.target else Path.cwd()
    if not target.is_dir():
        print(f"ERROR: target is not a directory: {target}", file=sys.stderr)
        return 1
    if not TEMPLATE_ROOT.is_dir():
        print(f"ERROR: template not found: {TEMPLATE_ROOT}", file=sys.stderr)
        return 1
    result = init_layer(target, TEMPLATE_ROOT, args.with_skills, args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for rel in result["created"]:
            print(f"created  {rel}")
        for rel in result["skipped"]:
            print(f"skipped  {rel}")
    print(
        "Suggestion: register the PKB layer (inbox/, logs/, Templates/, "
        "Objetivos.md, index.md) in your project's CLAUDE.md. "
        "I do not edit CLAUDE.md.",
        file=sys.stderr,
    )
    return 0


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # usage errors exit 2
        self.print_usage(sys.stderr)
        print(f"ERROR: {message}", file=sys.stderr)
        sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description="PKB layer tooling")
    sub = parser.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init", help="install the PKB layer")
    init.add_argument("--target", help="project root (default: cwd)")
    init.add_argument("--with-skills", action="store_true",
                      help="also copy the 5 PKB skills into <target>/.claude/skills/")
    init.add_argument("--dry-run", action="store_true")
    init.add_argument("--json", action="store_true")
    init.set_defaults(func=_cmd_init)
    cap = sub.add_parser("capture", help="write the inbox note for one skill invocation")
    cap.add_argument("--skill", required=True)
    cap.add_argument("--artifact", required=True)
    cap.add_argument("--session-id", required=True)
    cap.add_argument("--brief")
    cap.add_argument("--target", help="project root (default: cwd)")
    cap.add_argument("--json", action="store_true")
    cap.set_defaults(func=_cmd_capture)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

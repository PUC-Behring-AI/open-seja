#!/usr/bin/env python3
# designer: I install the personal-knowledge layer (inbox, logs, note
#   templates, index) in your project without overwriting anything you
#   already wrote. I tell you which files I created and which I skipped, and
#   I never edit your CLAUDE.md: I only suggest the line to add.
"""
pkb_inbox.py -- PKB layer tooling (init).

Invocation: agent-invoked, user-invoked via /seja-setup --pkb
Lifecycle: active

Usage:
    pkb_inbox.py init [--target DIR] [--with-skills] [--dry-run] [--json]

Exit codes: 0 ok, 1 error, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

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
    pairs.append((None, target / "logs" / str(date.today().year) / ".gitkeep"))
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
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

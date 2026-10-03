#!/usr/bin/env python3
# designer: When an agent executes your plan step by step, I make it leave a short,
#   fixed-form note per step -- what happened, what deviated, what it is less sure
#   about, and what the quality gate said -- so that what it learned does not vanish
#   when the session ends, and so /reflect can hand it back to you as evidence.
"""
step_notes — Per-step reflection-on-action notes in the plan progress file.

Invocation: skill-invoked, library
Lifecycle: active

Writes and reads a fixed-form note block in ``${PLANS_DIR}/plan-<id>-progress.md``:

    ### Step <N> -- reflection-on-action | <YYYY-MM-DD HH:MM UTC> | <title>
    - happened: <txt>
    - deviated: <txt|none>
    - less-sure: <txt|none>
    - gate: <PASS|FAIL|ERROR> (exit <n>, attempts <k>, <path>) | not-installed | not-run
    - human: "<verbatim>"            (only with --human)

Subcommands:
    append        append one note (creates the progress file when missing)
    parse         read the notes back (--json, --stats)
    reflect-bullet  append a dated aggregate bullet to the plan's ## Reflection

Exit codes: 0 ok, 2 refused (nothing written).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import project_config  # noqa: E402

REPO_ROOT = project_config.REPO_ROOT

PROGRESS_HEADER = """# Progress -- Plan {plan_id}

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log
"""

GATE_FLAGS = ("not-installed", "not-run")
_NOTE_HEADER_RE = re.compile(
    r"^### Step (?P<step>\d+) -- reflection-on-action \| (?P<dt>[^|]+?) \| (?P<title>.*)$"
)
_FIELD_RE = re.compile(r"^- (happened|deviated|less-sure|gate|human): ?(.*)$")
_GATE_LINE_RE = re.compile(
    r"^(?P<status>[A-Z]+) \(exit (?P<exit>-?\d+), attempts (?P<att>\d+), (?P<path>.*)\)$"
)


class StepNotesError(Exception):
    """Refused input; nothing was written."""


@dataclass
class StepNote:
    step: int
    datetime: str
    title: str
    happened: str = ""
    deviated: str = ""
    less_sure: str = ""
    gate_status: str | None = None  # PASS|FAIL|ERROR|not-installed|not-run
    gate_exit: int | None = None
    gate_attempts: int | None = None
    gate_path: str | None = None
    human: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _plans_dir() -> Path:
    return project_config.get_path("PLANS_DIR", "_output/plans") or (
        REPO_ROOT / "_output" / "plans"
    )


def _norm_id(plan_id: str) -> str:
    return plan_id.zfill(6) if plan_id.isdigit() else plan_id


def progress_path(plan_id: str, plans_dir: Path | None = None) -> Path:
    return (plans_dir or _plans_dir()) / f"plan-{_norm_id(plan_id)}-progress.md"


def plan_path(plan_id: str, plans_dir: Path | None = None) -> Path:
    d = plans_dir or _plans_dir()
    nid = _norm_id(plan_id)
    matches = sorted(
        p for p in d.glob(f"plan-{nid}-*.md") if not p.name.endswith("-progress.md")
    )
    if not matches:
        raise StepNotesError(f"plan file for {nid} not found in {d}")
    return matches[0]


def _normalize(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace."""
    return " ".join(re.sub(r"[^\w\s]", " ", text.lower()).split())


def _one_line(text: str) -> str:
    return " ".join(text.split())


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _read_gate_json(path: Path, attempts: int | None) -> tuple[str, int, int, str]:
    if not path.is_file():
        raise StepNotesError(f"--gate-json not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise StepNotesError(f"--gate-json is not valid JSON: {path}") from err
    if not isinstance(data, dict) or data.get("version") != 1:
        raise StepNotesError(f"--gate-json is not a version 1 gate result: {path}")
    status = str(data.get("status", "")).upper()
    exit_code = data.get("exit_code")
    if not status or not isinstance(exit_code, int):
        raise StepNotesError(f"--gate-json lacks status/exit_code: {path}")
    resolved = path.resolve()
    try:
        shown = str(resolved.relative_to(Path(REPO_ROOT).resolve()))
    except ValueError:
        shown = str(resolved)
    return status, exit_code, attempts if attempts is not None else 1, shown


# ---------------------------------------------------------------------------
# Library API
# ---------------------------------------------------------------------------


def append_note(
    plan_id: str,
    step: int,
    title: str,
    happened: str,
    deviated: str,
    less_sure: str,
    gate_json: Path | None = None,
    gate_attempts: int | None = None,
    human: str | None = None,
    gate: str | None = None,
    plans_dir: Path | None = None,
    now: str | None = None,
) -> Path:
    """Append a note block to the plan's progress file and return its path."""
    happened, deviated, less_sure = (_one_line(x) for x in (happened, deviated, less_sure))
    title = _one_line(title)
    if not happened or _normalize(happened) == _normalize(title):
        raise StepNotesError("happened must be non-empty and differ from the step title")
    if not deviated or not less_sure:
        raise StepNotesError("deviated and less-sure must be non-empty (use 'none')")
    if (gate_json is None) == (gate is None):
        raise StepNotesError("give exactly one of --gate-json or --gate")
    if gate is not None:
        if gate not in GATE_FLAGS:
            raise StepNotesError(f"--gate must be one of {', '.join(GATE_FLAGS)}")
        gate_line = gate
    else:
        assert gate_json is not None
        status, code, att, shown = _read_gate_json(gate_json, gate_attempts)
        gate_line = f"{status} (exit {code}, attempts {att}, {shown})"

    lines = [
        f"### Step {step} -- reflection-on-action | {now or _now()} | {title}",
        f"- happened: {happened}",
        f"- deviated: {deviated}",
        f"- less-sure: {less_sure}",
        f"- gate: {gate_line}",
    ]
    if human is not None:
        lines.append(f'- human: "{_one_line(human)}"')
    block = "\n".join(lines) + "\n"

    path = progress_path(plan_id, plans_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(PROGRESS_HEADER.format(plan_id=_norm_id(plan_id)), encoding="utf-8")
    with path.open("rb") as fh:
        content = fh.read()
    prefix = b"" if content.endswith(b"\n") or not content else b"\n"
    with path.open("ab") as fh:
        fh.write(prefix + b"\n" + block.encode("utf-8"))
    return path


def parse_notes(text: str) -> list[StepNote]:
    """Extract note blocks in file order, ignoring everything else."""
    notes: list[StepNote] = []
    current: StepNote | None = None
    for line in text.splitlines():
        m = _NOTE_HEADER_RE.match(line)
        if m:
            current = StepNote(int(m["step"]), m["dt"].strip(), m["title"].strip())
            notes.append(current)
            continue
        if current is None:
            continue
        f = _FIELD_RE.match(line)
        if not f:
            current = None  # block ends at the first non-field line
            continue
        key, val = f.group(1), f.group(2).strip()
        if key == "happened":
            current.happened = val
        elif key == "deviated":
            current.deviated = val
        elif key == "less-sure":
            current.less_sure = val
        elif key == "human":
            current.human = val[1:-1] if len(val) >= 2 and val[0] == val[-1] == '"' else val
        elif key == "gate":
            g = _GATE_LINE_RE.match(val)
            if g:
                current.gate_status = g["status"]
                current.gate_exit = int(g["exit"])
                current.gate_attempts = int(g["att"])
                current.gate_path = g["path"]
            else:
                current.gate_status = val
    return notes


def _is_none(text: str) -> bool:
    return _normalize(text) in ("", "none")


def stats(notes: list[StepNote]) -> dict[str, int]:
    seen: dict[str, int] = {}
    for n in notes:
        k = _normalize(n.happened)
        seen[k] = seen.get(k, 0) + 1
    return {
        "notes": len(notes),
        "with_deviation": sum(1 for n in notes if not _is_none(n.deviated)),
        "with_gate": sum(1 for n in notes if n.gate_exit is not None),
        "both_none": sum(1 for n in notes if _is_none(n.deviated) and _is_none(n.less_sure)),
        "duplicate_happened": sum(1 for c in seen.values() if c > 1),
    }


def reflect_bullet(
    plan_id: str,
    synthesis: str,
    plans_dir: Path | None = None,
    today: str | None = None,
) -> Path:
    """Insert a dated aggregate bullet in the plan's ## Reflection (create at EOF)."""
    synthesis = _one_line(synthesis)
    if not synthesis:
        raise StepNotesError("synthesis must be non-empty")
    prog = progress_path(plan_id, plans_dir)
    notes = parse_notes(prog.read_text(encoding="utf-8")) if prog.is_file() else []
    s = stats(notes)
    bullet = (
        f"- {today or datetime.now(timezone.utc).strftime('%Y-%m-%d')}: {synthesis} "
        f"(notes {s['notes']}, with deviation {s['with_deviation']}, with gate {s['with_gate']})\n"
    )
    plan = plan_path(plan_id, plans_dir)
    lines = plan.read_text(encoding="utf-8").splitlines(keepends=True)

    start = next((i for i, ln in enumerate(lines) if ln.rstrip() == "## Reflection"), None)
    if start is None:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines += ["\n", "## Reflection\n", "\n", bullet]
    else:
        end = next(
            (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
            len(lines),
        )
        last_bullet = max(
            (i for i in range(start + 1, end) if lines[i].startswith("- ")), default=None
        )
        if last_bullet is None:
            pos = max(
                (i for i in range(start + 1, end) if lines[i].strip()), default=start
            ) + 1
        else:
            pos = last_bullet + 1
            while pos < end and lines[pos].startswith((" ", "\t")) and lines[pos].strip():
                pos += 1
        if pos > 0 and not lines[pos - 1].endswith("\n"):
            lines[pos - 1] += "\n"
        if last_bullet is None and pos == start + 1:
            lines.insert(pos, "\n")
            pos += 1
        lines.insert(pos, bullet)
    plan.write_text("".join(lines), encoding="utf-8")
    return plan


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("append", help="append a reflection-on-action note")
    a.add_argument("--plan", required=True)
    a.add_argument("--step", required=True, type=int)
    a.add_argument("--title", required=True)
    a.add_argument("--happened", required=True)
    a.add_argument("--deviated", required=True)
    a.add_argument("--less-sure", required=True, dest="less_sure")
    a.add_argument("--gate-json", type=Path)
    a.add_argument("--gate", choices=GATE_FLAGS)
    a.add_argument("--gate-attempts", type=int)
    a.add_argument("--human")

    r = sub.add_parser("parse", help="read notes from a progress file")
    r.add_argument("progress_file", type=Path)
    r.add_argument("--json", action="store_true", dest="as_json")
    r.add_argument("--stats", action="store_true")

    b = sub.add_parser("reflect-bullet", help="append aggregate bullet to ## Reflection")
    b.add_argument("--plan", required=True)
    b.add_argument("--synthesis", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.cmd == "append":
            path = append_note(
                args.plan, args.step, args.title, args.happened, args.deviated,
                args.less_sure, args.gate_json, args.gate_attempts, args.human,
                gate=args.gate,
            )
            print(path)
        elif args.cmd == "reflect-bullet":
            print(reflect_bullet(args.plan, args.synthesis))
        else:
            if not args.progress_file.is_file():
                raise StepNotesError(f"progress file not found: {args.progress_file}")
            notes = parse_notes(args.progress_file.read_text(encoding="utf-8"))
            st = stats(notes) if args.stats else None
            if args.as_json:
                out: object = [asdict(n) for n in notes]
                if st is not None:
                    out = {"notes": out, "stats": st}
                print(json.dumps(out, ensure_ascii=False, indent=2))
            else:
                for n in notes:
                    print(f"step {n.step} | {n.title} | gate: {n.gate_status}")
                if st is not None:
                    print(
                        f"notes {st['notes']}, with deviation {st['with_deviation']}, "
                        f"with gate {st['with_gate']}, both none {st['both_none']}, "
                        f"duplicate happened {st['duplicate_happened']}"
                    )
    except StepNotesError as err:
        print(f"step_notes: {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

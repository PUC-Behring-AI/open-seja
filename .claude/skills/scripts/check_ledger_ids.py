#!/usr/bin/env python3
# designer: When two people on your team create artifacts on their own
#   machines, I check that no two plans, reports or reflections ended up
#   with the same ID, that every birth record in _output/ids/ is coherent
#   and points to an artifact, and that no pending action or design
#   decision number was created twice. I tell you which files collide
#   before you commit, instead of letting them coexist in silence.
"""
check_ledger_ids.py -- Detect duplicate and orphan IDs in the SEJA ledger.

Invocation: agent-invoked, hook-ci
Lifecycle: active

Checks (D-010):
  1. duplicate-id: two primary artifacts in ``OUTPUT_DIR/**/*.md`` with the
     same ID in the file name (the type may be hyphenated, e.g.
     ``mob-session-<id>-<slug>.md``) (companions ``<type>-<id>-qa-*.md`` and
     ``<type>-<id>-progress.md`` share the ID of their primary and are skipped).
     Two birth records in ``ids/`` with the same ``id`` also count.
  2. orphan-record: ``ids/<uid>.json`` whose ``id`` has no artifact and whose
     ``ts_utc`` is older than ``--orphan-days`` (default 7). Warning; error
     with ``--strict``.
  3. duplicate-pa: two records in ``pending.jsonl`` with the same ``id`` that
     both carry ``created_at`` (creation records; updates carry only
     ``id``/``status``/``closed_at`` or ``snooze_until``).
  4. duplicate-decision: two ``### D-NNN:`` headings with the same number in
     the ``## Decisions`` section of ``product-design-as-intended.md``.
  5. duplicate-uid: two birth records with the same ``uid``.
  6. incoherent-id: a birth record whose ``id`` differs from
     ``artifact_id.visible_id(uid)``, whose uid is not a ULID, or whose file
     name is not ``<uid>.json``; unreadable records are reported here too.

When the output directory does not exist (project without a ledger), exits 0
with no output.

Exit codes: 0 = no errors (warnings allowed), 1 = errors found, 2 = usage error.

Usage
-----
    python .claude/skills/scripts/check_ledger_ids.py
    python .claude/skills/scripts/check_ledger_ids.py --output-dir _output --strict
    python .claude/skills/scripts/check_ledger_ids.py --orphan-days 14 --json

CHECK_PLUGIN_MANIFEST:
  name: Ledger IDs
  stack:
    backend: [any]
    frontend: [any]
  scope: ledger
  critical: true
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from artifact_id import ARTIFACT_ID, normalize_id, visible_id

SCHEMA_VERSION = 1
DEFAULT_ORPHAN_DAYS = 7
DESIGN_REL = Path("product-design") / "product-design-as-intended.md"

# <type>-<id>[-<rest>].md ; <type> may be hyphenated (mob-session,
# dev-onboarding, data-model). The type is letters only, so it never swallows
# digits; the lookahead keeps the legacy alternative from matching the first
# six digits of a new-format ID.
_NAME_RE = re.compile(
    rf"^([a-z]+(?:-[a-z]+)*?)-({ARTIFACT_ID})(?![0-9A-Za-z])(?:-(.*))?\.md\Z"
)
_DECISION_RE = re.compile(r"^###\s+D-(\d+):")
_H2_RE = re.compile(r"^##\s")


def _finding(kind: str, message: str, **extra: object) -> dict:
    return {"kind": kind, "message": message, **extra}


def _is_companion(rest: str | None) -> bool:
    if rest is None:
        return False
    return rest == "progress" or rest == "qa" or rest.startswith("qa-")


def scan_artifacts(output_dir: Path) -> dict[str, list[str]]:
    """Map each artifact ID to the primary artifact paths (relative, posix) that use it."""
    by_id: dict[str, list[str]] = defaultdict(list)
    ids_dir = output_dir / "ids"
    for path in sorted(output_dir.rglob("*.md")):
        if ids_dir in path.parents:
            continue
        m = _NAME_RE.match(path.name)
        if not m or _is_companion(m.group(3)):
            continue
        by_id[normalize_id(m.group(2))].append(path.relative_to(output_dir).as_posix())
    return by_id


def all_artifact_ids(output_dir: Path) -> set[str]:
    """IDs of every artifact file, primary or companion."""
    found: set[str] = set()
    for path in output_dir.rglob("*.md"):
        m = _NAME_RE.match(path.name)
        if m:
            found.add(normalize_id(m.group(2)))
    return found


def check_duplicate_artifacts(by_id: dict[str, list[str]]) -> list[dict]:
    return [
        _finding(
            "duplicate-id",
            f"ID {aid} used by {len(paths)} artifacts: {', '.join(paths)}",
            id=aid,
            paths=paths,
        )
        for aid, paths in sorted(by_id.items())
        if len(paths) > 1
    ]


def _load_record(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _parse_ts(raw: object) -> datetime | None:
    if not isinstance(raw, str):
        return None
    try:
        ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def _record_coherence(path: Path, rec: dict | None) -> str | None:
    """Return a problem description for an incoherent record, else None."""
    if rec is None:
        return "unreadable birth record"
    uid = rec.get("uid")
    if not isinstance(uid, str):
        return "birth record without uid"
    try:
        expected = visible_id(uid)
    except ValueError:
        return f"uid {uid!r} is not a ULID"
    if rec.get("id") != expected:
        return f"id {rec.get('id')!r} != visible_id({uid}) = {expected!r}"
    if path.stem != uid:
        return f"file name {path.name} does not match uid {uid}"
    return None


def check_records(
    output_dir: Path, artifact_ids: set[str], orphan_days: int, now: datetime
) -> tuple[list[dict], list[dict]]:
    """Checks 1 (record side), 2, 5 and 6 over ``ids/*.json``."""
    errors: list[dict] = []
    orphans: list[dict] = []
    ids_dir = output_dir / "ids"
    if not ids_dir.is_dir():
        return errors, orphans
    by_uid: dict[str, list[str]] = defaultdict(list)
    by_vid: dict[str, list[str]] = defaultdict(list)
    cutoff = now - timedelta(days=orphan_days)
    for path in sorted(ids_dir.glob("*.json")):
        rel = path.relative_to(output_dir).as_posix()
        rec = _load_record(path)
        problem = _record_coherence(path, rec)
        if problem:
            errors.append(_finding("incoherent-id", f"{rel}: {problem}", paths=[rel]))
        if rec is None:
            continue
        uid, vid = rec.get("uid"), rec.get("id")
        if isinstance(uid, str):
            by_uid[uid].append(rel)
        if not isinstance(vid, str):
            continue
        by_vid[vid].append(rel)
        ts = _parse_ts(rec.get("ts_utc"))
        if vid not in artifact_ids and ts is not None and ts < cutoff:
            orphans.append(
                _finding(
                    "orphan-record",
                    f"{rel}: id {vid} has no artifact (born {rec.get('ts_utc')})",
                    id=vid,
                    paths=[rel],
                )
            )
    for uid, paths in sorted(by_uid.items()):
        if len(paths) > 1:
            errors.append(
                _finding("duplicate-uid", f"uid {uid} in {', '.join(paths)}", id=uid, paths=paths)
            )
    for vid, paths in sorted(by_vid.items()):
        if len(paths) > 1:
            errors.append(
                _finding(
                    "duplicate-id",
                    f"ID {vid} claimed by {len(paths)} birth records: {', '.join(paths)}",
                    id=vid,
                    paths=paths,
                )
            )
    return errors, orphans


def check_pending(pending_file: Path) -> list[dict]:
    """Check 3: two creation records (with ``created_at``) for the same ``pa-`` id."""
    if not pending_file.is_file():
        return []
    created: dict[str, list[int]] = defaultdict(list)
    lines = pending_file.read_text(encoding="utf-8", errors="replace").splitlines()
    for lineno, line in enumerate(lines, start=1):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict) and isinstance(rec.get("id"), str) and "created_at" in rec:
            created[rec["id"]].append(lineno)
    return [
        _finding(
            "duplicate-pa",
            f"{pid} created {len(nums)} times in pending.jsonl (lines {', '.join(map(str, nums))})",
            id=pid,
            paths=["pending.jsonl"],
        )
        for pid, nums in sorted(created.items())
        if len(nums) > 1
    ]


def check_decisions(design_file: Path) -> list[dict]:
    """Check 4: duplicate ``### D-NNN:`` headings inside ``## Decisions``."""
    if not design_file.is_file():
        return []
    seen: dict[int, list[int]] = defaultdict(list)
    in_section = False
    lines = design_file.read_text(encoding="utf-8", errors="replace").splitlines()
    for lineno, line in enumerate(lines, start=1):
        if _H2_RE.match(line):
            in_section = line.strip() == "## Decisions"
            continue
        m = _DECISION_RE.match(line) if in_section else None
        if m:
            seen[int(m.group(1))].append(lineno)
    return [
        _finding(
            "duplicate-decision",
            f"D-{num:03d} appears {len(nums)} times in ## Decisions "
            f"(lines {', '.join(map(str, nums))})",
            id=f"D-{num:03d}",
            paths=[design_file.name],
        )
        for num, nums in sorted(seen.items())
        if len(nums) > 1
    ]


def run(
    output_dir: Path,
    design_file: Path,
    orphan_days: int,
    strict: bool,
    now: datetime | None = None,
) -> dict:
    """Run all checks; return the report dict (schema_version 1)."""
    now = now or datetime.now(timezone.utc)
    errors = check_duplicate_artifacts(scan_artifacts(output_dir))
    record_errors, orphans = check_records(
        output_dir, all_artifact_ids(output_dir), orphan_days, now
    )
    errors += record_errors
    errors += check_pending(output_dir / "pending.jsonl")
    errors += check_decisions(design_file)
    warnings: list[dict] = []
    if strict:
        errors += orphans
    else:
        warnings += orphans
    return {"schema_version": SCHEMA_VERSION, "errors": errors, "warnings": warnings}


def _print_text(report: dict) -> None:
    print("# Ledger ID Check\n")
    for f in report["errors"]:
        print(f"  ERROR [{f['kind']}]: {f['message']}")
    for f in report["warnings"]:
        print(f"  WARNING [{f['kind']}]: {f['message']}")
    if report["errors"] or report["warnings"]:
        print()
    print(f"Errors: {len(report['errors'])}  Warnings: {len(report['warnings'])}")


def _default_output_dir() -> Path:
    from project_config import REPO_ROOT, get_path

    return get_path("OUTPUT_DIR") or (REPO_ROOT / "_output")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect duplicate and orphan IDs in the SEJA ledger"
    )
    parser.add_argument("--output-dir", type=Path, help="ledger root (default: OUTPUT_DIR)")
    parser.add_argument(
        "--orphan-days",
        type=int,
        default=DEFAULT_ORPHAN_DAYS,
        help=f"age in days after which a record without artifact is reported (default {DEFAULT_ORPHAN_DAYS})",
    )
    parser.add_argument("--strict", action="store_true", help="orphan records are errors")
    parser.add_argument("--json", action="store_true", help="JSON output with schema_version")
    parser.add_argument(
        "--design-file",
        type=Path,
        help="as-intended file (default: <output-dir>/../product-design/product-design-as-intended.md)",
    )
    args = parser.parse_args(argv)
    if args.orphan_days < 0:
        parser.error("--orphan-days must be >= 0")

    output_dir = args.output_dir if args.output_dir is not None else _default_output_dir()
    if not output_dir.is_dir():
        return 0
    design_file = args.design_file or (output_dir.resolve().parent / DESIGN_REL)

    report = run(output_dir, design_file, args.orphan_days, args.strict)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text(report)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())

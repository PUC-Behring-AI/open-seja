#!/usr/bin/env python3
# designer: When a skill is about to create a new plan, research report, or any other
#   artifact, I'm the one that gives it an identity. I mint a ULID on your machine,
#   without asking anyone, and write its birth record to _output/ids/, one file per
#   artifact. Two devs on different machines never collide, because each ID is born
#   from a local ULID, and I never touch your artifact index. You get back the short
#   ID (date plus six characters) that the skill writes into the filename and header.
"""
reserve_id.py -- ULID-based identity for SEJA artifacts, with a birth record per artifact.

Invocation: skill-invoked
Lifecycle: active

Generates a ULID locally (no coordination, no network; D-010), derives the
visible ID ``YYYYMMDD-xxxxxx`` from it, and writes the birth record to
``<output-dir>/ids/<uid>.json`` (tempfile + os.replace). INDEX.md is neither
read nor written: it is fully derived by generate_macro_index.py.

stdout carries only the visible ID (skills capture it), or the full birth
record with --json. ``uid: <ULID>`` goes to stderr for information.
The author is a pseudonymous token (artifact_id.default_author()), overridable
by --author with another token (12 lowercase hex chars or ``unknown``); free
text is refused with exit 2, and it is never ``git config user.name``
(constitution C2).

Exit codes: 0 reserved (or dry run); 2 usage error (e.g., invalid --origin or --author).

Usage
-----
    python3 .claude/skills/scripts/reserve_id.py --type research --title "Some title"
    python3 .claude/skills/scripts/reserve_id.py --type plan --title "T" --origin research-NNNNNN
    python3 .claude/skills/scripts/reserve_id.py --type plan --title "T" --dry-run
    python3 .claude/skills/scripts/reserve_id.py --type plan --title "T" --json

Run from the repository root.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

from artifact_id import ARTIFACT_ID, birth_record
from project_config import REPO_ROOT, get_path

_DEFAULT_OUTPUT_DIR = get_path("OUTPUT_DIR") or REPO_ROOT / "_output"

# Module-level default; overridden by --output-dir when called from CLI.
OUTPUT_DIR = _DEFAULT_OUTPUT_DIR

ORIGIN_RE = re.compile(rf"^[a-z][a-z-]*-{ARTIFACT_ID}\Z")
# Pseudonymous token only (constitution C2): never a free-text name.
AUTHOR_RE = re.compile(r"^(?:[0-9a-f]{12}|unknown)\Z")


def _write_record_atomic(ids_dir: Path, record: dict) -> Path:
    """Write the birth record to ids_dir/<uid>.json via tempfile + os.replace."""
    ids_dir.mkdir(parents=True, exist_ok=True)
    target = ids_dir / f"{record['uid']}.json"
    fd, tmp_path = tempfile.mkstemp(dir=str(ids_dir), prefix=".id_", suffix=".tmp")
    tmp = Path(tmp_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(record, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(str(tmp), str(target))
    except Exception:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        raise
    return target


def reserve(
    artifact_type: str,
    title: str,
    origin: str | None = None,
    author: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Mint a new artifact identity and return its birth record.

    Unless dry_run, the record is written to OUTPUT_DIR/ids/<uid>.json.
    """
    record = birth_record(artifact_type, title, author, origin)
    if not dry_run:
        _write_record_atomic(OUTPUT_DIR / "ids", record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reserve a new artifact ID (ULID-based) and write its birth record"
    )
    parser.add_argument(
        "--type", required=True, dest="artifact_type",
        help="Artifact type (e.g., research, plan, check, advisory [legacy read alias])",
    )
    parser.add_argument(
        "--title", required=True,
        help="Short descriptive title for the artifact",
    )
    parser.add_argument(
        "--origin",
        help="Artifact this one derives from, as <type>-<id> (e.g., research-YYYYMMDD-xxxxxx)",
    )
    parser.add_argument(
        "--author",
        help=(
            "Pseudonymous author token: 12 lowercase hex chars or 'unknown' "
            "(default: artifact_id.default_author()); never a name"
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print a new ID without writing the birth record",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Print the full birth record as JSON instead of the visible ID",
    )
    parser.add_argument(
        "--output-dir",
        help="Override OUTPUT_DIR (write ids/<uid>.json under this directory)",
    )
    args = parser.parse_args()

    if args.origin is not None and not ORIGIN_RE.match(args.origin):
        parser.error(f"invalid --origin {args.origin!r}: expected <type>-<id>, e.g. plan-YYYYMMDD-xxxxxx")
    if args.author is not None and not AUTHOR_RE.match(args.author):
        # Do not echo the value: it may be a person's name (constitution C2).
        parser.error("invalid --author: expected 12 lowercase hex chars or 'unknown'")

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir).resolve()

    record = reserve(
        args.artifact_type,
        args.title,
        origin=args.origin,
        author=args.author,
        dry_run=args.dry_run,
    )
    print(f"uid: {record['uid']}", file=sys.stderr)
    if args.as_json:
        print(json.dumps(record, ensure_ascii=False))
    else:
        print(record["id"])


if __name__ == "__main__":
    main()

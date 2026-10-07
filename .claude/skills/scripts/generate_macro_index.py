#!/usr/bin/env python3
# designer: When you finish any skill run that writes an artifact, I'm the
#   indexer that refreshes `_output/INDEX.md` so you can find the new file
#   without scanning directories -- every plan, advisory, roadmap, proposal,
#   communication, onboarding, reflection, mob session, and explain report (behavior,
#   behavior-evolution, dev-onboarding, data-model, architecture) appears on
#   one chronological list, newest first. IDs reserved for artifacts not yet
#   written show up as RESERVED rows, read from their birth records, so I hold
#   no state of my own and you can regenerate me at any time.
"""
generate_macro_index.py -- Unified artifact index generator.

Invocation: skill-invoked, user-cli
Lifecycle: active

Recursively scans all .md files in the project's OUTPUT_DIR and subfolders,
extracts metadata (date, type, title) from each file's header, and generates
OUTPUT_DIR/INDEX.md with all artifacts sorted in descending chronological order
(newest first).

INDEX.md is fully derived (D-010, plan-000019). RESERVED rows come from the
birth records that reserve_id.py writes to OUTPUT_DIR/ids/<uid>.json: one row
per record whose ID has no artifact file yet. Rows of a previous INDEX.md are
never preserved. Both ID formats are accepted in headers: legacy six digits
(``000007``) and the ULID-derived visible ID (``20261007-k3m9qz``).

The output directory is read from product-design/conventions.md (the OUTPUT_DIR
variable), making this script portable across any SEJA-bootstrapped project.

Usage
-----
    python .claude/skills/scripts/generate_macro_index.py
    python .claude/skills/scripts/generate_macro_index.py --verbose

``--finalize ID`` is deprecated and a no-op (INDEX.md is derived; regenerate).

Run from the repository root.
"""

# Rationale for design choices and historical context: see generate_macro_index-rationale.md in this directory.
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from artifact_id import ARTIFACT_ID, ULID_ID, normalize_id
from project_config import REPO_ROOT, get_path

OUTPUT_DIR = get_path("OUTPUT_DIR") or REPO_ROOT / "_output"
INDEX_FILE = OUTPUT_DIR / "INDEX.md"

# Files to exclude from indexing (basenames)
EXCLUDED_FILES = {
    "INDEX.md",
    "briefs.md",
    "briefs-index.md",
}


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text to max_len, appending ellipsis if needed."""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "\u2026"


# ---------------------------------------------------------------------------
# Date extraction helpers
# ---------------------------------------------------------------------------
_DATETIME_RE = re.compile(r"(\d{4}-\d{2}-\d{2}[\s]+\d{2}:\d{2}(?::\d{2})?(?:\s*UTC)?)")
_DATE_ONLY_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_FILENAME_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _normalize_date(date_str: str) -> str:
    """Normalize a date string for consistent sorting."""
    date_str = date_str.strip()
    # Pad to full datetime if only date
    if len(date_str) == 10:  # YYYY-MM-DD
        return date_str + " 00:00:00 UTC"
    return date_str


# ---------------------------------------------------------------------------
# Extractors for known artifact types
# ---------------------------------------------------------------------------

# ID field of an H1: legacy six digits, ULID-derived visible ID, or any digits
# (very old headers such as "Plan 7").
_ID = rf"({ARTIFACT_ID}|\d+)"
# Optional "METACOMM |" field after the PREFIX-SCOPE of plan headers.
_METACOMM_OPT = r"(?:METACOMM\s*\|\s*)?"
# Companion QA log of a plan: plan-<id>-qa-<slug>.md
_PLAN_QA_FILE_RE = re.compile(rf"^plan-{ARTIFACT_ID}-qa-")
# Standalone DONE marker that /implement writes above the plan H1.
_DONE_MARKER_RE = re.compile(r"^#\s+DONE\s*\|\s*[\d\-: UTC]+\|\s*$", re.IGNORECASE)

# Plan (done): # DONE | datetime | Plan NNNN | PREFIX-SCOPE | datetime | title
_PLAN_DONE_RE = re.compile(
    rf"^#\s+DONE\s*\|\s*([\d\-: UTC]+)\s*\|\s*Plan\s+{_ID}\s*\|\s*(\S+)\s*\|\s*{_METACOMM_OPT}([\d\-: UTC]+)\s*\|\s*([^|]+)",
    re.IGNORECASE,
)

# Plan (open): # Plan NNNN | PREFIX-SCOPE | datetime | title
_PLAN_OPEN_RE = re.compile(
    rf"^#\s+Plan\s+{_ID}\s*\|\s*(\S+)\s*\|\s*{_METACOMM_OPT}([\d\-: UTC]+)\s*\|\s*([^|]+)",
    re.IGNORECASE,
)

# Plan (alt done): # Plan NNNN | DONE | PREFIX-SCOPE | datetime | title
_PLAN_ALT_DONE_RE = re.compile(
    rf"^#\s+Plan\s+{_ID}\s*\|\s*DONE\s*\|\s*(\S+)\s*\|\s*{_METACOMM_OPT}([\d\-: UTC]+)\s*\|\s*([^|]+)",
    re.IGNORECASE,
)

# Advisory: # Advisory NNNN | PREFIX-SCOPE | datetime | title
_ADVISORY_RE = re.compile(
    rf"^#\s+Advisory\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Research: # Research NNNN | PREFIX-SCOPE | datetime | title
_RESEARCH_RE = re.compile(
    rf"^#\s+Research\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Proposal: # Proposal NNNN | PREFIX-SCOPE | datetime | title
_PROPOSAL_RE = re.compile(
    rf"^#\s+Proposal\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Roadmap: # Roadmap NNNN | datetime | title
_ROADMAP_RE = re.compile(
    rf"^#\s+Roadmap\s+{_ID}\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# QA Session: # QA Session - datetime  (em dash or hyphen)
_QA_SESSION_RE = re.compile(
    r"^#\s+QA\s+Session\s*[\u2014\-]+\s*([\d\-: UTC]+)",
    re.IGNORECASE,
)

# QA Log (dated): # QA Log | <parent-ref> | datetime | title
# New canonical format with datetime as the third pipe field
_QA_LOG_DATED_RE = re.compile(
    r"^#\s+QA\s+Log\s*\|\s*(.+?)\s*\|\s*(\d{4}-\d{2}-\d{2}[\s\d:]*(?:UTC)?)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# QA Log (plan) with pipe: # QA Log | Plan NNNN | title  OR  # QA Log | implement NNNN, NNNN
_QA_LOG_PLAN_PIPE_RE = re.compile(
    rf"^#\s+QA\s+Log\s*\|\s*(?:implement\s+)?(?:Plan\s+)?({ULID_ID}|\d[\d\-,\s]*)(?:\s*\|\s*(.+))?\s*$",
    re.IGNORECASE,
)

# QA Log (plan) with dash/em-dash: # QA Log — Plan NNNN — title
_QA_LOG_PLAN_DASH_RE = re.compile(
    rf"^#\s+QA\s+Log\s*[\u2014\-]+\s*(?:Post-skill\s+for\s+)?(?:Plan[s]?\s+)?({ULID_ID}|\d[\d\-,\s]*)\s*[\u2014\-]+\s*(.+)",
    re.IGNORECASE,
)

# QA Log (skill): # QA Log | skill | brief
_QA_LOG_SKILL_RE = re.compile(
    r"^#\s+QA\s+Log\s*\|\s*(\S+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# QA Log generic (catch-all for variations like "Post-skill for Plans")
_QA_LOG_GENERIC_RE = re.compile(
    r"^#\s+QA\s+Log\s*[\u2014\-|:]+\s*(.+)",
    re.IGNORECASE,
)

# Metacomm: # Metacommunication Message — title  OR  # Metacommunication Message (subtitle)
_METACOMM_RE = re.compile(
    r"^#\s+Metacommunication\s+Message\s*(?:[\u2014\-]+\s*)?(.+)",
    re.IGNORECASE,
)

# Check log: # Check <id> | PREFIX-SCOPE | datetime | title
_CHECK_LOG_RE = re.compile(
    rf"^#\s+Check\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Reflection: # Reflection <id> | datetime | title
_REFLECTION_RE = re.compile(
    rf"^#\s+Reflection\s+{_ID}\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Mob Session: # Mob Session <id> | datetime | title  (${MOB_SESSIONS_DIR})
_MOB_SESSION_RE = re.compile(
    rf"^#\s+Mob\s+Session\s+{_ID}\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Behavior Evolution: # Behavior Evolution <id> | <PREFIX-SCOPE> | <datetime> | <title>
_BEHAVIOR_EVOLUTION_RE = re.compile(
    rf"^#\s+Behavior\s+Evolution\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Behavior: # Behavior <id> | <PREFIX-SCOPE> | <datetime> | <title>
_BEHAVIOR_RE = re.compile(
    rf"^#\s+Behavior\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Dev-Onboarding: # Dev-Onboarding <id> | <PREFIX-SCOPE> | <datetime> | <title>
_DEV_ONBOARDING_RE = re.compile(
    rf"^#\s+Dev-Onboarding\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Data Model: # Data Model <id> | <PREFIX-SCOPE> | <datetime> | <title>
_DATA_MODEL_RE = re.compile(
    rf"^#\s+Data\s+Model\s+{_ID}\s*\|\s*(\S+)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)

# Architecture: # Architecture <id> | <scope-descriptor> | <datetime> | <title>
# Scope is a multi-word text descriptor (e.g. "entire system"), not a PREFIX-SCOPE token.
_ARCHITECTURE_RE = re.compile(
    rf"^#\s+Architecture\s+{_ID}\s*\|\s*(.+?)\s*\|\s*([\d\-: UTC]+)\s*\|\s*(.+)",
    re.IGNORECASE,
)


def _find_date_in_text(text: str) -> str | None:
    """Try to find a date in the first 10 lines of text."""
    for line in text.split("\n")[:10]:
        m = _DATETIME_RE.search(line)
        if m:
            return m.group(1).strip()
    for line in text.split("\n")[:10]:
        m = _DATE_ONLY_RE.search(line)
        if m:
            return m.group(1).strip()
    return None


def _find_date_in_filename(filename: str) -> str | None:
    """Try to extract a date from filename."""
    m = _FILENAME_DATE_RE.search(filename)
    if m:
        return m.group(1).strip()
    return None


def _find_date_from_mtime(filepath: Path) -> str | None:
    """Last-resort: use file modification time as date."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    except OSError:
        return None


def extract_artifact(filepath: Path) -> dict | None:
    """Extract artifact metadata from a markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    # Find the first heading line
    headings = [
        line.strip() for line in text.split("\n")[:5] if line.strip().startswith("#")
    ]
    if not headings:
        return None
    header_line = headings[0]
    # /implement writes "# DONE | <datetime> |" on its own line above the plan H1;
    # join the two so the single-line DONE pattern applies.
    if _DONE_MARKER_RE.match(header_line) and len(headings) > 1:
        header_line = f"{header_line.rstrip()} {headings[1].lstrip('#').strip()}"

    rel_path = filepath.relative_to(OUTPUT_DIR)

    # Try each known pattern

    # Plan (done)
    m = _PLAN_DONE_RE.match(header_line)
    if m:
        status = "DONE"
        plan_id = normalize_id(m.group(2).strip())
        is_qa = bool(_PLAN_QA_FILE_RE.match(filepath.name))
        return {
            "date": _normalize_date(m.group(4).strip()),
            "type": "Plan QA" if is_qa else "Plan",
            "id": plan_id,
            "title": truncate(m.group(5).strip().rstrip("|").strip()),
            "status": status,
            "file": str(rel_path),
        }

    # Plan (alt done): # Plan NNNN | DONE | PREFIX-SCOPE | datetime | title
    m = _PLAN_ALT_DONE_RE.match(header_line)
    if m:
        plan_id = normalize_id(m.group(1).strip())
        is_qa = bool(_PLAN_QA_FILE_RE.match(filepath.name))
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Plan QA" if is_qa else "Plan",
            "id": plan_id,
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Plan (open)
    m = _PLAN_OPEN_RE.match(header_line)
    if m:
        plan_id = normalize_id(m.group(1).strip())
        is_qa = bool(_PLAN_QA_FILE_RE.match(filepath.name))
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Plan QA" if is_qa else "Plan",
            "id": plan_id,
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "OPEN",
            "file": str(rel_path),
        }

    # Advisory
    m = _ADVISORY_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Advisory",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Research (forward-only advisory-to-research rename target)
    m = _RESEARCH_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Research",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Proposal
    m = _PROPOSAL_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Proposal",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "OPEN",
            "file": str(rel_path),
        }

    # Roadmap
    m = _ROADMAP_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(2).strip()),
            "type": "Roadmap",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(3).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # QA Session
    m = _QA_SESSION_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(1).strip()),
            "type": "QA Session",
            "id": "",
            "title": truncate(header_line.lstrip("# ").strip()),
            "status": "",
            "file": str(rel_path),
        }

    # QA Log (dated): # QA Log | <parent-ref> | datetime | title
    m = _QA_LOG_DATED_RE.match(header_line)
    if m:
        # Extract ID from parent ref (e.g., "Advisory 000058" -> "000058")
        parent_ref = m.group(1).strip()
        id_match = re.search(rf"({ULID_ID}|\d{{3,6}})", parent_ref)
        qa_id = normalize_id(id_match.group(1).strip()) if id_match else ""
        return {
            "date": _normalize_date(m.group(2).strip()),
            "type": "QA Log",
            "id": qa_id,
            "title": truncate(m.group(3).strip().rstrip("|").strip()),
            "status": "",
            "file": str(rel_path),
        }

    # QA Log (plan, pipe separator)
    m = _QA_LOG_PLAN_PIPE_RE.match(header_line)
    if m:
        date = _find_date_in_text(text) or _find_date_in_filename(filepath.name) or _find_date_from_mtime(filepath) or ""
        title_raw = m.group(2).strip().rstrip("|").strip() if m.group(2) else f"QA for plan {m.group(1).strip()}"
        return {
            "date": _normalize_date(date) if date else "",
            "type": "QA Log",
            "id": m.group(1).strip(),
            "title": truncate(title_raw),
            "status": "",
            "file": str(rel_path),
        }

    # QA Log (plan, dash/em-dash separator)
    m = _QA_LOG_PLAN_DASH_RE.match(header_line)
    if m:
        date = _find_date_in_text(text) or _find_date_in_filename(filepath.name) or _find_date_from_mtime(filepath) or ""
        return {
            "date": _normalize_date(date) if date else "",
            "type": "QA Log",
            "id": m.group(1).strip(),
            "title": truncate(m.group(2).strip().rstrip("|").strip()),
            "status": "",
            "file": str(rel_path),
        }

    # QA Log (skill)
    m = _QA_LOG_SKILL_RE.match(header_line)
    if m:
        date = _find_date_in_text(text) or _find_date_in_filename(filepath.name) or _find_date_from_mtime(filepath) or ""
        return {
            "date": _normalize_date(date) if date else "",
            "type": "QA Log",
            "id": "",
            "title": truncate(m.group(2).strip().rstrip("|").strip()),
            "status": "",
            "file": str(rel_path),
        }

    # QA Log (generic catch-all)
    m = _QA_LOG_GENERIC_RE.match(header_line)
    if m:
        date = _find_date_in_text(text) or _find_date_in_filename(filepath.name) or _find_date_from_mtime(filepath) or ""
        return {
            "date": _normalize_date(date) if date else "",
            "type": "QA Log",
            "id": "",
            "title": truncate(m.group(1).strip().rstrip("|").strip()),
            "status": "",
            "file": str(rel_path),
        }

    # Metacomm
    m = _METACOMM_RE.match(header_line)
    if m:
        date = _find_date_in_text(text) or _find_date_in_filename(filepath.name) or _find_date_from_mtime(filepath) or ""
        return {
            "date": _normalize_date(date) if date else "",
            "type": "Metacomm",
            "id": "",
            "title": truncate(m.group(1).strip()),
            "status": "",
            "file": str(rel_path),
        }

    # Check log
    m = _CHECK_LOG_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Check",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Reflection
    m = _REFLECTION_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(2).strip()),
            "type": "Reflection",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(3).strip().rstrip("|").strip()),
            "status": "",
            "file": str(rel_path),
        }

    # Mob Session
    m = _MOB_SESSION_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(2).strip()),
            "type": "Mob Session",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(3).strip().rstrip("|").strip()),
            "status": "",
            "file": str(rel_path),
        }

    # Behavior Evolution (before Behavior)
    m = _BEHAVIOR_EVOLUTION_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Behavior Evolution",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Behavior
    m = _BEHAVIOR_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Behavior",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Dev-Onboarding
    m = _DEV_ONBOARDING_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Dev-Onboarding",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Data Model
    m = _DATA_MODEL_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Data Model",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Architecture (scope is free-text descriptor, not a PREFIX-SCOPE token)
    m = _ARCHITECTURE_RE.match(header_line)
    if m:
        return {
            "date": _normalize_date(m.group(3).strip()),
            "type": "Architecture",
            "id": normalize_id(m.group(1).strip()),
            "title": truncate(m.group(4).strip().rstrip("|").strip()),
            "status": "DONE",
            "file": str(rel_path),
        }

    # Fallback: try to extract date from text, filename, or mtime
    date = _find_date_in_text(text) or _find_date_in_filename(filepath.name) or _find_date_from_mtime(filepath)
    if date:
        title = header_line.lstrip("# ").strip()
        return {
            "date": _normalize_date(date),
            "type": "Other",
            "id": "",
            "title": truncate(title),
            "status": "",
            "file": str(rel_path),
        }

    return None


# ---------------------------------------------------------------------------
# RESERVED rows (derived from birth records, never from a previous INDEX.md)
# ---------------------------------------------------------------------------


def _format_ts(ts_utc: str) -> str:
    """Render an ISO-8601 birth timestamp as ``YYYY-MM-DD HH:MM UTC``."""
    try:
        dt = datetime.fromisoformat(ts_utc)
    except (TypeError, ValueError):
        return ""
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _reserved_from_ids_dir(scanned_ids: set[str], verbose: bool = False) -> list[dict]:
    """Return one RESERVED entry per birth record in OUTPUT_DIR/ids/ with no artifact.

    Unreadable or malformed records are skipped with a warning on stderr; the
    ledger checker (check_ledger_ids.py) is the place that reports them.
    """
    ids_dir = OUTPUT_DIR / "ids"
    if not ids_dir.is_dir():
        return []
    reserved: list[dict] = []
    for fp in sorted(ids_dir.glob("*.json")):
        try:
            record = json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"WARNING: skipping birth record {fp.name}: {exc}", file=sys.stderr)
            continue
        rid = record.get("id") if isinstance(record, dict) else None
        if not isinstance(rid, str) or not rid:
            print(f"WARNING: skipping birth record {fp.name}: no id", file=sys.stderr)
            continue
        if rid in scanned_ids:
            if verbose:
                print(f"  RESERVED {rid} has its artifact, not listed")
            continue
        reserved.append({
            "date": _format_ts(record.get("ts_utc", "")),
            "type": "RESERVED",
            "id": rid,
            "title": truncate(f"{record.get('type', '')}: {record.get('title', '')}"),
            "status": "RESERVED",
            "file": "",
        })
    return reserved


def generate_index(verbose: bool = False) -> int:
    """Generate INDEX.md from all artifact files. Returns count of indexed entries."""
    if not OUTPUT_DIR.is_dir():
        print(f"ERROR: Output directory not found: {OUTPUT_DIR}")
        return 0

    # Collect all .md files recursively, excluding specific files
    md_files = sorted(
        f
        for f in OUTPUT_DIR.rglob("*.md")
        if f.is_file()
        and f.name not in EXCLUDED_FILES
    )

    entries = []
    scanned_ids: set[str] = set()
    for fp in md_files:
        entry = extract_artifact(fp)
        if entry:
            entries.append(entry)
            if entry["id"]:
                scanned_ids.add(entry["id"])
            if verbose:
                print(f"  Indexed: [{entry['type']}] {entry.get('id', '')} -- {entry['title']}")
        elif verbose:
            print(f"  Skipped (no match): {fp.relative_to(OUTPUT_DIR)}")

    # RESERVED rows: birth records whose ID has no artifact file yet
    entries.extend(_reserved_from_ids_dir(scanned_ids, verbose=verbose))

    # Sort by date descending (newest first), entries without dates go last
    entries.sort(key=lambda e: e["date"] if e["date"] else "", reverse=True)

    # Write INDEX.md
    lines = [
        "# Artifact Index",
        "",
        f"> Auto-generated by `generate_macro_index.py`. {len(entries)} artifacts indexed (newest first).",
        "> Do not edit manually -- regenerate with: `python .claude/skills/scripts/generate_macro_index.py`",
        "",
        "| Date | Type | ID | Title | Status | File |",
        "|------|------|----|-------|--------|------|",
    ]

    for e in entries:
        file_link = e["file"].replace("\\", "/")
        if file_link:
            file_cell = f"[{Path(e['file']).name}]({file_link})"
        else:
            file_cell = ""
        lines.append(
            f"| {e['date']} | {e['type']} | {e['id']} | {e['title']} | {e['status']} | {file_cell} |"
        )

    lines.append("")
    INDEX_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"Generated {INDEX_FILE.relative_to(REPO_ROOT)} with {len(entries)} entries.")
    return len(entries)


_FINALIZE_DEPRECATED = "deprecated: INDEX.md is derived; just regenerate"


def finalize_reserved(artifact_id: str, status: str, verbose: bool = False) -> bool:
    """Deprecated no-op (plan-000019): INDEX.md is fully derived.

    RESERVED rows disappear on their own once the artifact file exists, so
    there is nothing to finalize. Kept so old invocations exit 0.
    """
    print(f"{_FINALIZE_DEPRECATED} (--finalize {artifact_id})", file=sys.stderr)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Unified artifact index generator for OUTPUT_DIR"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show each file being processed",
    )
    parser.add_argument(
        "--finalize", metavar="ID",
        help="Deprecated no-op: INDEX.md is derived; just regenerate",
    )
    parser.add_argument(
        "--status", choices=["DONE", "OPEN"], default="DONE",
        help="Deprecated; ignored (kept for old --finalize invocations)",
    )
    args = parser.parse_args()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

    if args.finalize:
        finalize_reserved(args.finalize, args.status, verbose=args.verbose)
    else:
        count = generate_index(verbose=args.verbose)
        if count == 0:
            sys.exit(1)


if __name__ == "__main__":
    main()

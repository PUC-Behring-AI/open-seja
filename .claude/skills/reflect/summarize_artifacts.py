#!/usr/bin/env python3
# designer: When /reflect anchors a reflection on a specific plan, advisory,
#   or other artifact, I'm the helper that resolves the ID or path and pulls
#   out the header metadata plus a short body excerpt. You get a compact
#   summary block the reflection can embed inline, so the rendered report
#   can point at the source artifact without dragging its full contents into
#   the prompt.
"""Summarize SEJA artifacts by ID or path for embedding in reflection reports.

Invocation: skill-invoked
Lifecycle: active
"""

# Rationale for design choices and historical context: see summarize_artifacts-rationale.md in this directory.
from __future__ import annotations

import re
import sys
from pathlib import Path

# Shared scripts (project_config, etc.) live in the sibling scripts/ directory
import sys as _sys; from pathlib import Path as _Path  # noqa: E702
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / 'scripts'))
del _sys, _Path
from project_config import REPO_ROOT, get_path  # noqa: E402
import step_notes  # noqa: E402
from artifact_id import ARTIFACT_ID

_HEADER_RE = re.compile(
    r"^#\s+(?:DONE\s*\|[^|]*\|)?\s*(?:Plan|Advisory|Reflection|Inventory|Proposal|Explained|Check)"
    rf"\s+({ARTIFACT_ID})\s*\|\s*([^|]*?)\s*\|(?:\s*METACOMM\s*\|)?\s*(\d{{4}}-\d{{2}}-\d{{2}}\s+\d{{2}}:\d{{2}}\s+UTC)\s*\|\s*(.+?)(?:\s*\|.*)?$",
    re.IGNORECASE,
)

_SCAN_DIRS = [
    "plans", "advisory-logs", "research-logs", "reflections", "inventories",
    "proposals", "explained-behaviors", "explained-code",
    "explained-data-model", "explained-architecture",
    "behavior-evolution", "check-logs",
]


def _is_companion(name: str) -> bool:
    """True for files that shadow a canonical artifact sharing the same id.

    Companion artifacts (progress logs, QA logs) live in the same directory as the
    canonical file and match the same bare id, so they must be excluded before any
    header-based tiebreak.
    """
    return name.endswith("-progress.md") or "-qa-" in name


_DONE_ONLY_RE = re.compile(r"^#\s+DONE\s*\|[^|]*\|\s*$")


def _header_line(lines: list[str]) -> str:
    """Return the header line, joining a DONE marker written on its own line.

    /implement may write ``# DONE | <date> |`` on a line of its own above the
    plan H1; joined, the two read like the single-line ``# DONE | ... | Plan ...``.
    """
    if not lines:
        return ""
    if len(lines) > 1 and _DONE_ONLY_RE.match(lines[0]):
        return f"{lines[0].rstrip()} {lines[1].lstrip('#').strip()}"
    return lines[0]


def _first_line(path: Path) -> str:
    """Return the header line of a file (see _header_line), or '' on error."""
    try:
        with path.open(encoding="utf-8") as fh:
            return _header_line([fh.readline().rstrip("\n"), fh.readline().rstrip("\n")])
    except OSError:
        return ""


def _pick_canonical(matches: list[Path]) -> Path:
    """Deterministically select the canonical artifact among id-matching files.

    Ordering: (1) PRIMARY -- drop companion suffixes (-progress.md / -qa-); (2)
    SECONDARY -- among survivors prefer the header-bearing file; (3) FALLBACK --
    first by name order if none survive (caller passes a name-sorted list, so
    this is deterministic). _HEADER_RE is deliberately NOT the sole
    discriminator: it does not enumerate the 'Research' token, so a research-log
    canonical file fails the header test -- companion-suffix exclusion is what
    protects research artifacts.
    """
    survivors = [f for f in matches if not _is_companion(f.name)] or matches
    for f in survivors:
        if _HEADER_RE.match(_first_line(f)):
            return f
    return survivors[0]


def _resolve_path(ref: str) -> Path | None:
    """Resolve an artifact reference (ID like 'plan-NNNNNN' or bare 'NNNNNN') to a file."""
    bare_id = re.sub(r"^(?:plan|advisory|research|reflection|inventory|proposal|check)-", "", ref)
    bare_id = bare_id.strip()
    output_dir = get_path("OUTPUT_DIR")
    for subdir in _SCAN_DIRS:
        d = output_dir / subdir
        if not d.is_dir():
            continue
        # sorted by name so the _pick_canonical fallback (survivors[0]) is
        # deterministic across platforms, not dependent on iterdir() order.
        matches = sorted(
            (f for f in d.iterdir() if f.suffix == ".md" and bare_id in f.name),
            key=lambda f: f.name,
        )
        if matches:
            return _pick_canonical(matches)
    p = Path(ref)
    if p.is_file():
        return p
    full = REPO_ROOT / ref
    if full.is_file():
        return full
    return None


def _extract_section(lines: list[str], heading_prefix: str, max_chars: int = 300) -> str:
    """Extract the first paragraph after a heading matching the prefix."""
    collecting = False
    buf: list[str] = []
    for line in lines:
        if line.startswith("#") and heading_prefix.lower() in line.lower():
            collecting = True
            continue
        if collecting:
            if line.startswith("#"):
                break
            stripped = line.strip()
            if stripped:
                buf.append(stripped)
            elif buf:
                break
    text = " ".join(buf)
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "..."
    return text


def summarize(artifact_refs: list[str]) -> list[dict]:
    """Return a list of summary dicts for each artifact reference."""
    results = []
    for ref in artifact_refs:
        path = _resolve_path(ref)
        if path is None:
            results.append({"id": ref, "error": "not found"})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            results.append({"id": ref, "error": f"could not read {path}"})
            continue
        lines = text.splitlines()
        header_match = _HEADER_RE.match(_header_line(lines)) if lines else None
        entry: dict = {
            "id": header_match.group(1) if header_match else ref,
            "type": _infer_type(path),
            "path": str(path.relative_to(REPO_ROOT)),
            "title": header_match.group(4).strip() if header_match else path.stem,
            "datetime": header_match.group(3) if header_match else "",
            "brief_excerpt": _extract_section(lines, "## User brief")
                or _extract_section(lines, "## Brief")
                or _extract_section(lines, "## What"),
            "interpretation_excerpt": _extract_section(lines, "## Agent interpretation")
                or _extract_section(lines, "## Problem"),
        }
        if entry["type"] == "plan":
            entry.update(_plan_evidence(path))
        results.append(entry)
    return results


_RECORD_RE = re.compile(r"^- (communication|drift): (.*?)\s*$")
_DETAIL_RE = re.compile(r"^(.*?)\s*\(([^()]*)\)$")


def _gate_json_exists(raw: str | None) -> bool:
    if not raw:
        return False
    p = Path(raw)
    return (p if p.is_absolute() else REPO_ROOT / p).is_file()


def _read_records(text: str) -> dict[str, str]:
    """Last ``- communication:`` / ``- drift:`` line wins (written by step_notes.py record)."""
    found: dict[str, str] = {}
    for line in text.splitlines():
        m = _RECORD_RE.match(line)
        if m:
            found[m.group(1)] = m.group(2)
    return found


def _communication_evidence(raw: str | None) -> dict:
    if raw is None:
        return {"status": "not-offered"}
    if raw == "declined":
        return {"status": "declined"}
    m = _DETAIL_RE.match(raw)
    path, segment = (m.group(1), m.group(2)) if m else (raw, "")
    return {"status": "recorded", "path": path, "segment": segment}


def _drift_evidence(raw: str | None) -> dict:
    if raw is None:
        return {"status": "not-offered"}
    if raw == "not-measured":
        return {"status": "not-measured"}
    m = _DETAIL_RE.match(raw)
    path, detail = (m.group(1), m.group(2)) if m else (raw, "")
    count = re.match(r"\s*(\d+)", detail)
    ev: dict = {"status": "recorded", "path": path, "items": int(count.group(1)) if count else None}
    full = Path(path) if Path(path).is_absolute() else REPO_ROOT / path
    ev["exists"] = full.is_file()
    if ev["exists"]:
        ev["header"] = _first_line(full)
    return ev


def _plan_evidence(plan_path: Path) -> dict:
    """Read the sibling progress file: step notes, gate, communication and drift evidence."""
    prog = plan_path.with_name(re.sub(rf"^(plan-{ARTIFACT_ID})(?![0-9A-Za-z]).*$", r"\1-progress.md", plan_path.name))
    text = ""
    if prog.is_file():
        try:
            text = prog.read_text(encoding="utf-8")
        except OSError:
            text = ""
    notes = step_notes.parse_notes(text)
    build = [n for n in notes if n.phase == "build"]
    records = _read_records(text)
    return {
        "step_notes": [
            {"step": n.step, "phase": n.phase, "deviated": n.deviated, "less_sure": n.less_sure,
             "gate_status": n.gate_status, "gate_attempts": n.gate_attempts}
            for n in notes
        ],
        "gate_evidence": {
            "total": len(build),
            "first_attempt_pass": sum(
                1 for n in build if n.gate_status == "PASS" and n.gate_attempts == 1),
            "steps": [
                {"step": n.step, "status": n.gate_status, "exit": n.gate_exit,
                 "attempts": n.gate_attempts, "path": n.gate_path,
                 "json_exists": _gate_json_exists(n.gate_path)}
                for n in build
            ],
        },
        "communication_evidence": _communication_evidence(records.get("communication")),
        "drift_evidence": _drift_evidence(records.get("drift")),
    }


def _infer_type(path: Path) -> str:
    name = path.parent.name
    mapping = {
        "plans": "plan", "advisory-logs": "advisory", "research-logs": "research",
        "reflections": "reflection",
        "inventories": "inventory", "proposals": "proposal", "check-logs": "check",
    }
    return mapping.get(name, "artifact")


def _steps(nums: list[int]) -> str:
    return ", ".join(str(n) for n in nums)


def _evidence_lines(s: dict) -> list[str]:
    """Markdown lines for plan evidence; agent words only appear quoted and attributed."""
    out: list[str] = []
    notes = s["step_notes"]
    if not notes:
        out.append("  - **Step notes**: no step notes recorded")
    else:
        deviated = [n["step"] for n in notes if not step_notes._is_none(n["deviated"])]
        line = f"  - **Step notes**: {len(notes)} notes"
        if deviated:
            line += f"; deviations in steps {_steps(deviated)}"
        out.append(line)
        for n in notes:
            if not step_notes._is_none(n["less_sure"]):
                label = "plan" if n["phase"] == "plan" else str(n["step"])
                out.append(f'    - step {label}, agent recorded (less sure): "{n["less_sure"]}"')
        g = s["gate_evidence"]
        if g["total"]:
            steps = g["steps"]
            bad = [x["step"] for x in steps if x["status"] in ("FAIL", "ERROR")]
            notrun = [x["step"] for x in steps if x["status"] == "not-run"]
            notinst = [x["step"] for x in steps if x["status"] == "not-installed"]
            line = f"  - **Gate evidence**: {g['first_attempt_pass']}/{g['total']} steps PASS on first attempt"
            if bad:
                line += f"; FAIL/ERROR in steps {_steps(bad)}"
            if notrun:
                line += f"; not-run in steps {_steps(notrun)}"
            if notinst:
                line += f"; not-installed in steps {_steps(notinst)}"
            out.append(line)
            for x in steps:
                if x["path"]:
                    link = f"[{x['path']}]({x['path']})" if x["json_exists"] else f"{x['path']} (json missing)"
                    out.append(f"    - step {x['step']}: {x['status']} (exit {x['exit']}, attempts {x['attempts']}), {link}")
    c = s["communication_evidence"]
    if c["status"] == "recorded":
        seg = c["segment"] or "segment unrecorded"
        out.append(f"  - **Communication evidence**: {seg}, [{c['path']}]({c['path']})")
    else:
        out.append(f"  - **Communication evidence**: {c['status'].replace('-', ' ')}")
    d = s["drift_evidence"]
    if d["status"] == "recorded":
        n = f"{d['items']} items" if d["items"] is not None else "items unrecorded"
        if d["exists"]:
            out.append(f"  - **Drift evidence**: {n}, [{d['path']}]({d['path']})")
            if d.get("header"):
                out.append(f'    - report header: "{d["header"]}"')
        else:
            out.append(f"  - **Drift evidence**: {n}, {d['path']} (report missing)")
    else:
        out.append(f"  - **Drift evidence**: {d['status'].replace('-', ' ')}")
    return out


def as_markdown_block(summaries: list[dict]) -> str:
    """Format summaries as a markdown bullet list for embedding in reports."""
    lines = []
    for s in summaries:
        if "error" in s:
            lines.append(f"- **{s['id']}** -- {s['error']}")
            continue
        lines.append(
            f"- [{s['type']}-{s['id']}]({s['path']}) | {s['datetime']} | {s['title']}"
        )
        if s.get("brief_excerpt"):
            lines.append(f"  - **Brief**: {s['brief_excerpt']}")
        if s.get("interpretation_excerpt"):
            lines.append(f"  - **Interpretation**: {s['interpretation_excerpt']}")
        if s.get("type") == "plan" and "step_notes" in s:
            lines.extend(_evidence_lines(s))
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: summarize_artifacts.py <id-or-path> [<id-or-path> ...]", file=sys.stderr)
        return 2
    refs = sys.argv[1:]
    summaries = summarize(refs)
    print(as_markdown_block(summaries))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for human_markers_registry.py (the real registry, not a patched copy)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
# tests/ -> scripts/ -> skills/ -> .claude/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[4]

sys.path.insert(0, str(SCRIPTS_DIR))

import human_markers_registry  # noqa: E402

AS_INTENDED = "product-design/product-design-as-intended.md"


def test_as_intended_is_human_markers_file():
    assert human_markers_registry.is_human_markers_file(AS_INTENDED) is True


def test_as_intended_windows_path_normalized():
    assert human_markers_registry.is_human_markers_file("product-design\\product-design-as-intended.md") is True


@pytest.mark.parametrize(
    "path",
    [
        "product-design/product-design-as-intended.md.bak",
        "docs/product-design-as-intended.md",
        "product-design-as-intended.md",
    ],
)
def test_lookalike_paths_are_not_registered(path):
    # Matching is exact-string, not suffix or basename based.
    assert human_markers_registry.is_human_markers_file(path) is False



# ---------------------------------------------------------------------------
# plan-000019 step 4: two plan-id formats and the DECISION_APPEND Source line
# ---------------------------------------------------------------------------

NEW_PLAN = "plan-20261007-k3m9qz"


def _matches(kind: str, line: str) -> bool:
    regex = human_markers_registry.ALLOWED_MARKERS[kind]["line_regex"]
    return re.fullmatch(regex, line) is not None


@pytest.mark.parametrize(
    ("kind", "line"),
    [
        ("STATUS", f"<!-- STATUS: implemented | {NEW_PLAN} | 2026-10-07 -->"),
        ("STATUS", "<!-- STATUS: implemented | plan-000265 | 2026-10-07 -->"),
        ("STATUS", "<!-- STATUS: implemented | manual | 2026-10-07 -->"),
        ("ESTABLISHED", f"<!-- ESTABLISHED: {NEW_PLAN} | 2026-10-07 -->"),
        ("INCORPORATED", f"<!-- INCORPORATED: {NEW_PLAN} | 2026-10-07 -->"),
        ("CHANGELOG_APPEND", f"2026-10-07 | R-P-001 | revised | {NEW_PLAN} | a note"),
        ("CHANGELOG_APPEND", "2026-10-07 | R-P-001 | revised | - | a note"),
    ],
)
def test_marker_regex_accepts_both_plan_formats(kind, line):
    assert _matches(kind, line)


@pytest.mark.parametrize(
    ("kind", "line"),
    [
        ("STATUS", "<!-- STATUS: implemented | plan-0007 | 2026-10-07 -->"),
        ("STATUS", "<!-- STATUS: implemented | plan-20261007-K3M9QZ | 2026-10-07 -->"),
        ("ESTABLISHED", "<!-- ESTABLISHED: plan-0007 | 2026-10-07 -->"),
        ("INCORPORATED", "<!-- INCORPORATED: plan-20261007-k3m9q | 2026-10-07 -->"),
        ("CHANGELOG_APPEND", "2026-10-07 | R-P-001 | revised | plan-0007 | a note"),
        ("CHANGELOG_APPEND", "2026-10-07 | R-P-001 | revised | manual | a note"),
    ],
)
def test_marker_regex_rejects_malformed_plan_ids(kind, line):
    assert not _matches(kind, line)


def test_decision_append_accepts_exact_source_line():
    assert _matches("DECISION_APPEND", "*Source: from research-000018 (2026-10-06)*")


@pytest.mark.parametrize(
    "line",
    [
        "*Source: texto livre sem data*",
        "*Source: note (2026-10-06)* trailing prose",
        "*Source: a *nested* note (2026-10-06)*",
        "*Source: <!-- STATUS: established --> (2026-10-06)*",
        "*Source:  (2026-10-06)*",
        "*Source: " + "x" * 201 + " (2026-10-06)*",
    ],
)
def test_decision_append_rejects_free_source_lines(line):
    assert not _matches("DECISION_APPEND", line)

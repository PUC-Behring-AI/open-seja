"""Tests for human_markers_registry.py (the real registry, not a patched copy)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
# tests/ -> scripts/ -> skills/ -> .claude/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[4]

sys.path.insert(0, str(SCRIPTS_DIR))

import human_markers_registry  # noqa: E402

SEJA_AS_INTENDED = "product-design/seja-as-intended.md"


def test_seja_as_intended_is_human_markers_file():
    assert human_markers_registry.is_human_markers_file(SEJA_AS_INTENDED) is True


def test_seja_as_intended_windows_path_normalized():
    assert human_markers_registry.is_human_markers_file("product-design\\seja-as-intended.md") is True


@pytest.mark.parametrize(
    "path",
    [
        "product-design/seja-as-intended.md.bak",
        "docs/seja-as-intended.md",
        "seja-as-intended.md",
    ],
)
def test_lookalike_paths_are_not_registered(path):
    # Matching is exact-string, not suffix or basename based.
    assert human_markers_registry.is_human_markers_file(path) is False


def test_seja_as_intended_entry_points_at_a_real_file():
    # Other product-design/ entries are seeded by /design and may legitimately be
    # absent in a given checkout; this fork-specific entry must not go dead.
    assert SEJA_AS_INTENDED in human_markers_registry.HUMAN_MARKERS_FILES
    assert (REPO_ROOT / SEJA_AS_INTENDED).is_file()

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


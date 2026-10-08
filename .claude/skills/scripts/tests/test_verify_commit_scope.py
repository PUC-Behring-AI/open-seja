"""Tests for verify_commit_scope.py (PKB prefix source and trailing-slash fix)."""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import verify_commit_scope as vcs

STAGED = ["inbox/2026-10-06-plan-000020-x.md", "inbox/_live.md"]


def _expected(always: list[str] | None = None) -> list[str]:
    return vcs.build_expected("unknown", "000020", None, always or [], None, None)


def test_pkb_notes_expected_when_layer_exists(tmp_path, monkeypatch):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "inbox" / "README.md").write_text("# inbox\n", encoding="utf-8")
    monkeypatch.setattr(vcs, "REPO_ROOT", tmp_path)
    result = vcs.check_scope(STAGED, _expected())
    assert result["unexpected"] == []
    assert result["pass"] is True


def test_pkb_notes_unexpected_without_layer(tmp_path, monkeypatch):
    monkeypatch.setattr(vcs, "REPO_ROOT", tmp_path)
    result = vcs.check_scope(STAGED, _expected())
    assert result["unexpected"] == STAGED
    assert result["pass"] is False


def test_always_include_directory_prefix_matches(tmp_path, monkeypatch):
    monkeypatch.setattr(vcs, "REPO_ROOT", tmp_path)
    expected = _expected(["docs/"])
    assert "docs/" in expected
    result = vcs.check_scope(["docs/a.md"], expected)
    assert result["unexpected"] == []


def test_normalize_keeps_trailing_slash():
    assert vcs._normalize("inbox/") == "inbox/"
    assert vcs._normalize("a/b.md") == "a/b.md"

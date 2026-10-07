"""Tests for pkb_inbox.py (init)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = SCRIPTS_DIR / "pkb_inbox.py"

sys.path.insert(0, str(SCRIPTS_DIR))

import pkb_inbox  # noqa: E402

TEMPLATE_ROOT = SCRIPTS_DIR.parent.parent / "references" / "template" / "pkb"


def _hashes(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_init_with_skills_creates_layer(tmp_path):
    result = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, False)
    assert (tmp_path / "inbox" / "README.md").is_file()
    assert len(list((tmp_path / "Templates").glob("*.md"))) == 6
    assert (tmp_path / ".claude" / "skills" / "daily-log" / "SKILL.md").is_file()
    assert (tmp_path / "inbox" / ".gitkeep").is_file()
    assert any((tmp_path / "logs").glob("*/.gitkeep"))
    assert result["created"] and result["skipped"] == []


def test_init_without_skills_leaves_claude_untouched(tmp_path):
    pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, False, False)
    assert not (tmp_path / ".claude").exists()
    assert (tmp_path / "Objetivos.md").is_file()


def test_init_is_idempotent(tmp_path):
    pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, False)
    before = _hashes(tmp_path)
    second = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, False)
    assert second["created"] == []
    assert second["skipped"]
    assert _hashes(tmp_path) == before


def test_init_preserves_existing_content(tmp_path):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "inbox" / "README.md").write_text("meu texto\n", encoding="utf-8")
    result = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, False, False)
    assert (tmp_path / "inbox" / "README.md").read_text(encoding="utf-8") == "meu texto\n"
    assert "inbox/README.md" in result["skipped"]


def test_dry_run_creates_nothing(tmp_path):
    result = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, True)
    assert result["created"]
    assert list(tmp_path.iterdir()) == []


def test_cli_json_and_usage(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "init", "--target", str(tmp_path), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema_version"] == 1
    assert "CLAUDE.md" in proc.stderr
    bad = subprocess.run([sys.executable, str(SCRIPT_PATH)], capture_output=True, text=True)
    assert bad.returncode == 2


def test_cli_missing_target_is_error(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "init", "--target", str(tmp_path / "nope")],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1


def test_pkb_dir_from_target_conventions(tmp_path):
    (tmp_path / "product-design").mkdir()
    (tmp_path / "product-design" / "conventions.md").write_text(
        "| `PKB_DIR` | `captura` | x |\n", encoding="utf-8")
    pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, False, False)
    assert (tmp_path / "captura" / "README.md").is_file()
    assert not (tmp_path / "inbox").exists()

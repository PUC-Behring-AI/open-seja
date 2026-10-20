"""Upgrade compatibility on two client fixtures (plan-20261020-688kjs Step 13).

client-v0.11.0: ladder files byte-identical to v0.11.0, one ladder file edited
by the client, features/, PKB_DIR filled and pkb_inbox.py.
client-v0.10.1: a client that never had the ladder.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_upgrade_compat

FIXTURES = Path(__file__).resolve().parent / "fixtures"
FEATURES_WARNING = "O ciclo não lê mais features/ nem .feature; nada foi apagado no seu projeto."
PKB_PREFIX = "A camada PKB saiu do harness"


def _ladder_warnings(report: dict) -> list[str]:
    return [w for w in report["warnings"] if w == FEATURES_WARNING or w.startswith(PKB_PREFIX)]


@pytest.fixture(scope="module")
def v0110(tmp_path_factory) -> dict:
    return run_upgrade_compat.run(FIXTURES / "client-v0.11.0", tmp_path_factory.mktemp("v0110"))


@pytest.fixture(scope="module")
def v0101(tmp_path_factory) -> dict:
    return run_upgrade_compat.run(FIXTURES / "client-v0.10.1", tmp_path_factory.mktemp("v0101"))


def test_v0101_client_gets_no_warning_and_nothing_removed(v0101) -> None:
    assert v0101["returncode"] == 0, v0101.get("stderr")
    assert v0101["removed"] == [] and v0101["kept"] == []
    assert _ladder_warnings(v0101) == []
    assert v0101["copied"]


def test_v0110_identical_ladder_files_are_removed(v0110) -> None:
    assert v0110["returncode"] == 0, v0110.get("stderr")
    target = Path(v0110["target"])
    expected = {
        ".claude/skills/scripts/check_specify.py",
        ".claude/references/general/grill-phase.md",
        ".claude/agents/scenario-tester.md",
        ".claude/references/template/feature-example/README.md",
        "tests/scenario_report.py",
    }
    assert set(v0110["removed"]) == expected
    assert not any((target / p).exists() for p in expected)
    assert not (target / ".claude/references/template/feature-example").exists()


def test_v0110_edited_ladder_file_is_kept(v0110) -> None:
    target = Path(v0110["target"])
    assert v0110["kept"] == [".claude/skills/scripts/check_intent.py"]
    assert (target / ".claude/skills/scripts/check_intent.py").read_text(encoding="utf-8").startswith(
        "# check_intent.py, edited by the client"
    )


def test_v0110_features_and_pkb_stay_and_both_warnings_appear(v0110) -> None:
    target = Path(v0110["target"])
    src = FIXTURES / "client-v0.11.0" / "features"
    for f in src.rglob("*"):
        if f.is_file():
            assert (target / "features" / f.relative_to(src)).read_bytes() == f.read_bytes()
    assert (target / ".claude/skills/scripts/pkb_inbox.py").is_file()
    warnings = _ladder_warnings(v0110)
    assert FEATURES_WARNING in warnings
    assert any(w.startswith(PKB_PREFIX) for w in warnings)


def test_fixture_itself_is_untouched(v0110) -> None:
    assert (FIXTURES / "client-v0.11.0/.claude/skills/scripts/check_specify.py").is_file()


def test_parse_output_reads_the_four_kinds() -> None:
    out = (
        "OK: Updated .claude/agents/a.md\n"
        "OK: removido .claude/x.py\n"
        "WARN: mantido (editado) .claude/y.py\n"
        "WARN: algo\n"
    )
    report = run_upgrade_compat.parse_output(out)
    assert report == {
        "removed": [".claude/x.py"],
        "kept": [".claude/y.py"],
        "copied": [".claude/agents/a.md"],
        "warnings": ["algo"],
    }

"""The four default-cycle checks inside run_all_checks.py (CYC-033, emenda 000015).

Invocation: test
Lifecycle: active

run_all_checks.py discovers every check_*.py by glob and runs it with no
arguments from the project root, reading only the exit code. These tests build
small throw-away projects (with `.claude` linked to this harness) and prove that
check_intent.py, check_features.py, check_specify.py and check_plan_scenarios.py
say "nada a verificar" and pass where there is no default cycle, fail with their
name where a feature or a v2 plan is broken, and never read a v1 plan beyond its
header. One full run_all_checks.py per project shape keeps the comparison honest:
apart from the four, every other check gives the same result in every shape.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS = _TESTS_DIR.parent
_CLAUDE = _SCRIPTS.parents[1]
_FIX = _TESTS_DIR / "fixtures"
FOUR = ("check_intent.py", "check_features.py", "check_specify.py", "check_plan_scenarios.py")
ROW = re.compile(r"^(check_\S+\.py)\s+(PASS|FAIL|ERROR)\s", re.MULTILINE)


def _project(tmp_path: Path, name: str) -> Path:
    root = tmp_path / name
    (root / "_output" / "plans").mkdir(parents=True)
    (root / ".claude").symlink_to(_CLAUDE, target_is_directory=True)
    for number, plan in enumerate(("v1-plan-with-tests.md", "v1-plan-doc-only.md"), start=1):
        shutil.copy(_FIX / "plan_format" / plan, root / "_output" / "plans" / f"plan-00000{number}-{plan}")
    return root


def _with_features(root: Path, source: Path) -> Path:
    shutil.copytree(source / "features", root / "features")
    return root


def _run_all(root: Path) -> dict[str, str]:
    run = subprocess.run([sys.executable, str(_SCRIPTS / "run_all_checks.py"), "--root", str(root)],
                         stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=200, check=False)
    rows = dict(ROW.findall(run.stdout))
    assert rows, run.stdout + run.stderr
    return rows


def _one(root: Path, script: str) -> tuple[int, str]:
    run = subprocess.run([sys.executable, str(_SCRIPTS / script)], cwd=root, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=120, check=False)
    return run.returncode, run.stdout + run.stderr


@pytest.fixture(scope="module")
def shapes(tmp_path_factory) -> dict[str, dict[str, str]]:
    """One full run_all_checks.py per project shape."""
    base = tmp_path_factory.mktemp("shapes")
    plain = _project(base, "sem-features-v1")
    third = _project(base, "features-de-terceiros")
    (third / "features" / "login").mkdir(parents=True)
    (third / "features" / "login" / "login.feature").write_text(
        "Feature: Login\n  Scenario: entra\n    Given a page\n", encoding="utf-8")
    approved = _with_features(_project(base, "feature-aprovada"), _FIX / "specify" / "spc-013-aprovado")
    return {"plain": _run_all(plain), "third": _run_all(third), "approved": _run_all(approved)}


def test_without_features_the_four_pass_and_say_nothing_to_check(tmp_path: Path) -> None:
    root = _project(tmp_path, "p")
    for script in FOUR:
        code, out = _one(root, script)
        assert code == 0 and "nada a verificar" in out, (script, out)


def test_run_all_checks_lists_the_four_as_pass_without_features(shapes) -> None:
    assert all(shapes["plain"][script] == "PASS" for script in FOUR)


def test_third_party_features_change_nothing(shapes, tmp_path: Path) -> None:
    assert shapes["third"] == shapes["plain"]
    root = _project(tmp_path, "t")
    (root / "features" / "login").mkdir(parents=True)
    (root / "features" / "login" / "login.feature").write_text("Feature: Login\n", encoding="utf-8")
    before = (root / "features" / "login" / "login.feature").read_bytes()
    for script in FOUR:
        assert _one(root, script)[0] == 0
    assert (root / "features" / "login" / "login.feature").read_bytes() == before


def test_valid_approved_feature_passes_and_nothing_else_moves(shapes) -> None:
    assert all(shapes["approved"][script] == "PASS" for script in FOUR)
    assert shapes["approved"] == shapes["plain"]


def test_feature_without_req_tag_fails_check_features(tmp_path: Path) -> None:
    root = _with_features(_project(tmp_path, "g"), _FIX / "features" / "ghk-002-sem-tag")
    code, out = _one(root, "check_features.py")
    assert code == 1 and "GHK-002" in out


def test_v2_plan_with_scenario_without_step_fails_check_plan_scenarios(tmp_path: Path) -> None:
    root = _with_features(_project(tmp_path, "v2"), _FIX / "plan_scenarios" / "_raizes" / "aprovada")
    shutil.copy(_FIX / "plan_scenarios" / "pfs-009-cenario-sem-step" / "plan.md",
                root / "_output" / "plans" / "plan-000009-cenario-sem-step.md")
    code, out = _one(root, "check_plan_scenarios.py")
    assert code == 1 and "PFS-009" in out


def test_only_v1_plans_are_never_read_past_the_header(tmp_path: Path) -> None:
    root = _project(tmp_path, "v1")
    shutil.copy(_FIX / "plan_scenarios" / "v1-corpo-quebrado" / "plan.md",
                root / "_output" / "plans" / "plan-000003-corpo-quebrado.md")
    code, out = _one(root, "check_plan_scenarios.py")
    assert code == 0 and "nada a verificar" in out
    run = subprocess.run([sys.executable, str(_SCRIPTS / "check_plan_scenarios.py"), "--json"], cwd=root,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120, check=False)
    assert json.loads(run.stdout)["plans"] == []


def test_the_four_are_in_the_registry_for_any_stack() -> None:
    registry = {e["script"]: e for e in json.loads((_SCRIPTS / "check_plugin_registry.json").read_text(encoding="utf-8"))}
    for script in FOUR:
        entry = registry[script]
        assert entry["stack"] == {"backend": ["any"], "frontend": ["any"]} and entry["critical"] is False

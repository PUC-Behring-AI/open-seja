"""Tests for the feature example and the Cucumber JSON -> DRM-003 state mapping (CYC-027).

Invocation: test
Lifecycle: active

Rules: .claude/references/general/gherkin-spec-format.md (section 8 and 10).
The files of the example have the suffix `.example`, so the harness pytest never collects them;
this test loads `cucumber_states.py.example` by path.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from check_features import main, parse_feature

_TESTS_DIR = Path(__file__).resolve().parent
_EXAMPLE = _TESTS_DIR.parents[2] / "references" / "template" / "feature-example"
_REPORT = _TESTS_DIR / "fixtures" / "runner" / "pytest-bdd-cucumber.json"


def _load_states():
    sys.dont_write_bytecode = True  # keep the reference folder free of __pycache__
    loader = importlib.machinery.SourceFileLoader("cucumber_states", str(_EXAMPLE / "cucumber_states.py.example"))
    spec = importlib.util.spec_from_loader("cucumber_states", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


states = _load_states()


def _element(*statuses: str, message: str = "") -> dict:
    steps = [{"name": f"s{i}", "result": {"status": s, **({"error_message": message} if s == "failed" else {})}}
             for i, s in enumerate(statuses)]
    return {"name": "X", "tags": [{"name": "REQ-x-001"}], "steps": steps}


# ---------------------------------------------------------------------------
# The example itself
# ---------------------------------------------------------------------------


def test_example_has_no_collectable_python_files() -> None:
    assert sorted(p.name for p in _EXAMPLE.glob("*.py")) == []
    assert (_EXAMPLE / "conftest.py.example").is_file() and (_EXAMPLE / "test_task_list.py.example").is_file()


def test_example_passes_the_validator(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(_EXAMPLE)]) == 0
    out = capsys.readouterr().out
    assert "0 erros, 1 aviso, 1 informação; 2 REQs, 4 cenários, 0 REQ sem cenário" in out


def test_example_has_no_partner_or_person_names() -> None:
    text = " ".join(p.read_text(encoding="utf-8") for p in _EXAMPLE.rglob("*") if p.is_file()).lower()
    assert "tecgraf" not in text and "petrobras" not in text


# ---------------------------------------------------------------------------
# Mapping table (gherkin-spec-format.md, section 8)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("element", "n_steps", "tags", "state"), [
    (_element("passed", "passed", "passed"), 3, [], "passed"),
    (_element("passed", "failed", message="E assert 1 == 2\ntest.py:8: AssertionError"), 3, [], "failed"),
    (_element("failed", message="RuntimeError: boom"), 3, [], "error"),
    (_element("passed", "ambiguous"), 2, [], "error"),
    (_element("passed", "undefined"), 2, [], "undefined"),
    (_element("passed", "pending"), 2, [], "undefined"),
    (_element("skipped", "skipped"), 2, [], "skipped"),
    (_element("passed"), 3, [], "undefined"),  # pytest-bdd leaves the undefined step out
    (_element("passed", "skipped"), 2, ["@xfail"], "xfail"),
    (_element("passed", "passed"), 2, ["@xfail"], "xfail"),  # xfail comes from the tag, whatever the result
])
def test_scenario_state_mapping(element: dict, n_steps: int, tags: list[str], state: str) -> None:
    assert states.scenario_state(element, n_steps, tags) == state


def test_scenario_key_uses_the_last_two_components_of_the_uri() -> None:
    assert states.scenario_key("features/login/a.feature", "Entrar") == "login/a.feature::Entrar"
    assert states.scenario_key("login/a.feature", "Entrar") == "login/a.feature::Entrar"


def test_missing_scenario_is_absent_or_skipped_by_its_tag() -> None:
    expected = {"s/a.feature::Um": {"steps": 3, "tags": ["@REQ-s-001"]},
                "s/a.feature::Dois": {"steps": 3, "tags": ["@REQ-s-001", "@skip"]}}
    assert states.report_states([], expected) == {"s/a.feature::Um": "absent", "s/a.feature::Dois": "skipped"}


def test_outline_is_the_worst_of_its_rows() -> None:
    report = [{"uri": "s/a.feature", "elements": [_element("passed") | {"name": "Esq"},
                                                  _element("failed", message="AssertionError") | {"name": "Esq"}]}]
    expected = {"s/a.feature::Esq": {"steps": 1, "tags": []}}
    assert states.report_states(report, expected) == {"s/a.feature::Esq": "failed"}


def test_real_pytest_bdd_report_maps_to_the_expected_states() -> None:
    report = json.loads(_REPORT.read_text(encoding="utf-8"))
    feature = parse_feature((_EXAMPLE / "features" / "task-list" / "manage-tasks.feature")
                            .read_text(encoding="utf-8"))
    expected = {states.scenario_key("features/task-list/manage-tasks.feature", sc.name):
                {"steps": len(sc.steps), "tags": [t.name for t in sc.tags]} for sc in feature.scenarios}
    prefix = "task-list/manage-tasks.feature::"
    assert states.report_states(report, expected) == {
        prefix + "Acrescentar uma tarefa": "passed",
        prefix + "Acrescentar tarefas de nomes diferentes": "passed",
        prefix + "Marcar uma tarefa como feita": "failed",
        prefix + "Desfazer a marcação de uma tarefa": "skipped",
    }


def test_report_carries_the_req_tag_of_every_scenario() -> None:
    report = json.loads(_REPORT.read_text(encoding="utf-8"))
    elements = [e for f in report for e in f["elements"]]
    assert elements and all(any(t["name"].startswith("REQ-") for t in e["tags"]) for e in elements)

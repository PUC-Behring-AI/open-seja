"""Tests for the pure logic of the runner report plugin (implement-test-first.md, ITF-016).

Invocation: test
Lifecycle: active

The plugin is a template for the project (`scenario_report.py.example`; the suffix keeps this
pytest from collecting it). It needs pytest-bdd only inside its hooks, so its pure functions are
loaded here by path and tested with the standard library. The run on a real pytest-bdd project is
in the progress file of plan-000013 (Step 4).
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import pytest
from check_features import scenario_key as features_key

_PLUGIN = (Path(__file__).resolve().parents[3] / "references" / "template" / "bdd" / "python"
           / "scenario_report.py.example")


def _load():
    sys.dont_write_bytecode = True
    loader = importlib.machinery.SourceFileLoader("scenario_report", str(_PLUGIN))
    spec = importlib.util.spec_from_loader("scenario_report", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


sr = _load()


def test_plugin_file_is_not_collectable() -> None:
    assert _PLUGIN.name.endswith(".py.example")
    assert not _PLUGIN.with_name("scenario_report.py").exists()


@pytest.mark.parametrize("slug,path,name", [
    ("task-list", "features/task-list/manage-tasks.feature", "Marcar uma tarefa como feita"),
    ("contas", "/abs/features/contas/a b.feature", "Ação com acento e espaços"),
    ("x", "x/y.feature", "nome com :: no meio"),
])
def test_key_is_the_same_as_check_features(slug: str, path: str, name: str) -> None:
    assert sr.scenario_key(slug, path, name) == features_key(slug, path, name)


def test_key_from_the_feature_path() -> None:
    assert sr.key_for("/proj/features/task-list/manage-tasks.feature", "Marcar uma tarefa como feita") == \
        "task-list/manage-tasks.feature::Marcar uma tarefa como feita"
    assert sr.key_for("C:\\proj\\features\\task-list\\a.feature", "X") == "task-list/a.feature::X"


def test_req_tags() -> None:
    assert sr.req_tags(["skip", "REQ-a-002", "@REQ-a-001", "nao-faz"]) == ["REQ-a-001", "REQ-a-002"]


@pytest.mark.parametrize("when,outcome,wasxfail,exc,expected", [
    ("call", "failed", False, "AssertionError", "failed"),
    ("call", "failed", False, "TypeError", "error"),
    ("setup", "failed", False, "AssertionError", "error"),
    ("call", "passed", False, None, "passed"),
    ("call", "skipped", True, None, "xfailed"),
    ("call", "passed", True, None, "xpassed"),
    ("setup", "skipped", False, None, "skipped"),
    ("call", "failed", False, "StepDefinitionNotFoundError", "error"),
])
def test_item_outcome(when: str, outcome: str, wasxfail: bool, exc: str | None, expected: str) -> None:
    assert sr.item_outcome(when, outcome, wasxfail, exc) == expected


def test_aggregate_outline_rows() -> None:
    assert sr.aggregate(["passed", "passed"]) == "passed"
    assert sr.aggregate(["passed", "failed"]) == "failed"
    assert sr.aggregate(["failed", "error"]) == "error"
    assert sr.aggregate(["passed", "skipped"]) == "skipped"
    assert sr.aggregate(["passed", "xfailed"]) == "xfailed"


def test_short_reason() -> None:
    assert sr.short_reason("assert False is True\n\nmore lines") == "assert False is True"
    assert len(sr.short_reason("x" * 500)) <= 200
    assert sr.short_reason(None) == ""


def test_add_row_builds_an_outline_record() -> None:
    records: dict = {}
    base = {"feature_file": "features/t/a.feature", "req": ["REQ-t-001"]}
    sr.add_row(records, "t/a.feature::O", dict(base, outcome="passed", exception=None, failing_step_type=None,
                                                 failing_step=None, step_func=None, reason="", undefined=False,
                                                 duration=0.1), index=0)
    sr.add_row(records, "t/a.feature::O", dict(base, outcome="failed", exception="AssertionError",
                                                 failing_step_type="then", failing_step="x", step_func=None,
                                                 reason="r", undefined=False, duration=0.2), index=1)
    rec = records["t/a.feature::O"]
    assert rec["outcome"] == "failed" and rec["exception"] == "AssertionError"
    assert [r["outcome"] for r in rec["rows"]] == ["passed", "failed"]
    assert rec["duration"] == pytest.approx(0.3)


def test_add_row_plain_scenario_has_no_rows() -> None:
    records: dict = {}
    sr.add_row(records, "t/a.feature::S", {"feature_file": "f", "req": [], "outcome": "passed", "exception": None,
                                           "failing_step_type": None, "failing_step": None, "step_func": None,
                                           "reason": "", "undefined": False, "duration": 0.0}, index=None)
    assert records["t/a.feature::S"]["rows"] is None


def test_build_report_header() -> None:
    report = sr.build_report({}, {"t::x": "passed"}, "9.0.0", "2026-10-06T18:00:00Z")
    assert report == {"schema_version": 1, "generated_at": "2026-10-06T18:00:00Z", "pytest_bdd_version": "9.0.0",
                      "scenarios": {}, "tests": {"t::x": "passed"}}


def test_selected_by_key() -> None:
    assert sr.selected("k1", include=["k1"], exclude=[]) is True
    assert sr.selected("k2", include=["k1"], exclude=[]) is False
    assert sr.selected("k1", include=[], exclude=["k1"]) is False
    assert sr.selected("k3", include=[], exclude=[]) is True

"""Tests for build_checks.py (implement-test-first.md, ITF-001..024).

Invocation: test
Lifecycle: active

Fixtures (fictitious) in fixtures/build/; one test per rule, positive and negative.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import build_checks as bc
import pytest

# Contract written before the code (plan-000013 step 3); removed when the module goes green (steps 4-6).
pytestmark = pytest.mark.xfail(reason="plan-000013 step 3: contrato antes do codigo", strict=False)


_FX = Path(__file__).resolve().parent / "fixtures" / "build"
_PROJECT = _FX / "project"
_PF = Path(__file__).resolve().parent / "fixtures" / "plan_format"
_PS = Path(__file__).resolve().parent / "fixtures" / "plan_scenarios"

K1 = "task-list/manage-tasks.feature::Acrescentar uma tarefa"
K2 = "task-list/manage-tasks.feature::Acrescentar tarefas de nomes diferentes"
K3 = "task-list/manage-tasks.feature::Marcar uma tarefa como feita"


def _report(name: str) -> dict:
    return json.loads((_FX / "reports" / f"{name}.json").read_text(encoding="utf-8"))


def _rules(result: dict) -> list[str]:
    return sorted({f["rule"] for f in result["findings"] if f["severity"] == "error"})


def _red(name: str, owned=(K3,), **kw) -> dict:
    kw.setdefault("root", _PROJECT)
    return bc.red_check(_report(name), list(owned), **kw)


# ---------------------------------------------------------------------------
# ITF-005 red-check (R1..R8) and ITF-006 record of the red
# ---------------------------------------------------------------------------


def test_red_ok_is_red_for_the_right_reason() -> None:
    result = _red("red-ok")
    assert result["ok"] is True
    assert _rules(result) == []
    red = result["scenarios"][K3]
    assert red["reason_ok"] is True
    assert red["outcome"] == "failed" and red["exception"] == "AssertionError"
    assert red["failing_step_type"] == "then"


@pytest.mark.parametrize("case", ["red-import-error", "red-collection-error", "red-undefined", "red-skipped", "red-xfail", "red-missing"])
def test_r1_outcome_not_failed(case: str) -> None:
    result = _red(case)
    assert result["ok"] is False
    assert "R1" in _rules(result)
    assert result["scenarios"][K3]["reason_ok"] is False


def test_r1_undefined_hint_names_the_step_definition() -> None:
    result = _red("red-undefined")
    hints = " ".join(f["hint"] for f in result["findings"])
    assert "definição" in hints


def test_r1_already_green_escalates() -> None:
    result = _red("red-already-green")
    assert result["ok"] is False
    assert "R1" in _rules(result)
    assert result["escalate"] is True
    assert result["scenarios"][K3]["already_green"] is True


def test_r2_exception_not_assertion() -> None:
    assert "R2" in _rules(_red("red-wrong-exception"))


@pytest.mark.parametrize("case", ["red-given-failure", "red-when-failure"])
def test_r3_failure_outside_then(case: str) -> None:
    result = _red(case)
    assert _rules(result) == ["R3"]


@pytest.mark.parametrize("case", ["red-constant-assert", "red-raise-assert"])
def test_r4_constant_assertion(case: str) -> None:
    assert _rules(_red(case)) == ["R4"]


def test_r4_conditional_raise_is_not_constant() -> None:
    assert _rules(_red("red-conditional-raise")) == []


def test_r5_skeleton_with_logic() -> None:
    result = _red("red-ok", skeleton_files=[_FX / "skeleton" / "invalid.py"])
    assert "R5" in _rules(result)
    assert _rules(_red("red-ok", skeleton_files=[_FX / "skeleton" / "valid.py"])) == []


def test_r6_suite_broken_by_a_non_owned_scenario() -> None:
    result = _red("red-suite-broken", baseline=_report("suite-base"))
    assert "R6" in _rules(result)


def test_r6_suite_broken_by_a_plain_test() -> None:
    assert "R6" in _rules(_red("red-suite-broken-test", baseline=_report("suite-base")))
    assert _rules(_red("red-ok", baseline=_report("suite-base"))) == []


def test_r7_code_of_the_step_not_exercised() -> None:
    cov = json.loads((_FX / "coverage" / "red-not-exercised.json").read_text(encoding="utf-8"))
    result = _red("red-ok", source_files=["src/tasks.py"], coverage=cov)
    assert "R7" in _rules(result)
    cov_ok = json.loads((_FX / "coverage" / "red-exercised.json").read_text(encoding="utf-8"))
    assert _rules(_red("red-ok", source_files=["src/tasks.py"], coverage=cov_ok)) == []


def test_r8_outline_partial_is_red_with_green_rows() -> None:
    result = _red("red-outline-partial", owned=(K2, K3))
    assert result["ok"] is True
    red = result["scenarios"][K2]
    assert red["rows_total"] == 3 and red["rows_failed"] == 2 and red["rows_green_in_red"] == 1


def test_r8_outline_with_error_row() -> None:
    result = _red("red-outline-error", owned=(K2,))
    assert result["ok"] is False
    assert "R8" in _rules(result)


def test_red_record_has_the_itf006_fields() -> None:
    red = _red("red-ok")["scenarios"][K3]
    for field in ("ts", "outcome", "reason_ok", "exception", "failing_step_type", "rows_total", "rows_failed",
                  "rows_green_in_red", "skeleton_files", "report"):
        assert field in red


def test_red_check_from_cucumber_json() -> None:
    cuke = json.loads((_FX / "cucumber" / "red-ok.cucumber.json").read_text(encoding="utf-8"))
    report = bc.report_from_cucumber(cuke)
    assert report["scenarios"][K3]["outcome"] == "failed"
    assert report["scenarios"][K3]["failing_step_type"] == "then"
    assert report["scenarios"][K2]["outcome"] == "passed"
    result = bc.red_check(report, [K3])
    assert result["ok"] is True
    infos = [f for f in result["findings"] if f["rule"] == "R4"]
    assert infos and infos[0]["severity"] == "info"  # no step function location: not verified


def test_red_check_from_cucumber_and_junit_undefined() -> None:
    cuke = json.loads((_FX / "cucumber" / "red-undefined.cucumber.json").read_text(encoding="utf-8"))
    junit = (_FX / "cucumber" / "red-undefined.junit.xml").read_text(encoding="utf-8")
    report = bc.report_from_cucumber(cuke, junit, expected={K3: 3})
    assert report["scenarios"][K3]["outcome"] == "error"
    assert report["scenarios"][K3]["undefined"] is True
    assert "R1" in _rules(bc.red_check(report, [K3]))


def test_cucumber_and_keyword_inherits_given() -> None:
    cuke = json.loads((_FX / "cucumber" / "red-given-and.cucumber.json").read_text(encoding="utf-8"))
    report = bc.report_from_cucumber(cuke)
    assert report["scenarios"][K3]["failing_step_type"] == "given"


def test_red_check_cli_exit_codes(tmp_path: Path) -> None:
    assert bc.main(["red-check", "--report", str(_FX / "reports" / "red-ok.json"), "--owned", K3,
                    "--root", str(_PROJECT), "--json"]) == 0
    assert bc.main(["red-check", "--report", str(_FX / "reports" / "red-import-error.json"), "--owned", K3]) == 1
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert bc.main(["red-check", "--report", str(bad), "--owned", K3]) == 2
    assert bc.main(["red-check", "--report", str(tmp_path / "absent.json"), "--owned", K3]) == 2


# ---------------------------------------------------------------------------
# ITF-004 skeleton
# ---------------------------------------------------------------------------


def test_skeleton_valid() -> None:
    assert bc.check_skeleton([_FX / "skeleton" / "valid.py"]) == []


def test_skeleton_with_logic() -> None:
    findings = bc.check_skeleton([_FX / "skeleton" / "invalid.py"])
    assert {f["rule"] for f in findings} == {"ITF-004"}
    lines = sorted(f["line"] for f in findings)
    assert lines == [5, 7, 15]  # the `if` and the call of total(), the call in calls()


# ---------------------------------------------------------------------------
# ITF-009 green-check
# ---------------------------------------------------------------------------


def test_green_ok() -> None:
    result = bc.green_check(_report("green-ok"), [K3])
    assert result["ok"] is True
    assert result["final"][K3]["test_result"] == "passed"


@pytest.mark.parametrize("case", ["green-skipped", "red-ok", "red-xfail", "red-missing"])
def test_green_not_passed(case: str) -> None:
    result = bc.green_check(_report(case), [K3])
    assert result["ok"] is False
    assert {f["rule"] for f in result["findings"]} == {"ITF-009"}


# ---------------------------------------------------------------------------
# ITF-007 freeze
# ---------------------------------------------------------------------------


def test_freeze_write_and_check(tmp_path: Path) -> None:
    (tmp_path / "features").mkdir()
    (tmp_path / "features" / "a.feature").write_text("Feature: x\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("def test_a():\n    assert 1\n", encoding="utf-8")
    snap = bc.freeze_snapshot(tmp_path, ["features/a.feature", "tests/test_a.py"])
    assert snap["schema_version"] == 1 and len(snap["files"]) == 2
    assert bc.freeze_compare(tmp_path, snap) == []
    (tmp_path / "tests" / "test_a.py").write_text("def test_a():\n    assert 2\n", encoding="utf-8")
    findings = bc.freeze_compare(tmp_path, snap)
    assert [(f["rule"], f["file"]) for f in findings] == [("ITF-007", "tests/test_a.py")]


def test_freeze_cli(tmp_path: Path) -> None:
    (tmp_path / "t.py").write_text("x = 1\n", encoding="utf-8")
    out = tmp_path / "snap.json"
    assert bc.main(["freeze", "--root", str(tmp_path), "--write", str(out), "t.py"]) == 0
    assert bc.main(["freeze", "--root", str(tmp_path), "--check", str(out)]) == 0
    (tmp_path / "t.py").write_text("x = 2\n", encoding="utf-8")
    assert bc.main(["freeze", "--root", str(tmp_path), "--check", str(out)]) == 1


# ---------------------------------------------------------------------------
# ITF-008 scope
# ---------------------------------------------------------------------------

_SCOPE = json.loads((_FX / "scope" / "cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _SCOPE, ids=[c["name"] for c in _SCOPE])
def test_scope_cases(case: dict) -> None:
    findings = bc.check_scope(case["role"], [tuple(c) for c in case["changes"]], set(case["frozen"]),
                              {k: v for k, v in case["added"].items()})
    got = sorted([f["rule"], f["file"]] for f in findings)
    assert got == sorted(case["expected"])


def test_scope_unknown_role() -> None:
    with pytest.raises(ValueError):
        bc.check_scope("architect", [], set(), {})


def test_scope_cli_on_a_git_repo(tmp_path: Path) -> None:
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True).stdout

    git("init", "-q")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base")
    base = git("rev-parse", "HEAD").strip()
    (tmp_path / "features").mkdir()
    (tmp_path / "features" / "a.feature").write_text("Feature: x\n", encoding="utf-8")
    assert bc.main(["scope", "--root", str(tmp_path), "--role", "coder", "--base", base]) == 1
    assert bc.main(["scope", "--root", str(tmp_path), "--role", "tester", "--base", base]) == 1
    (tmp_path / "features" / "a.feature").unlink()
    (tmp_path / "src.py").write_text("x = 1\n", encoding="utf-8")
    assert bc.main(["scope", "--root", str(tmp_path), "--role", "coder", "--base", base]) == 0


# ---------------------------------------------------------------------------
# ITF-018 uncovered
# ---------------------------------------------------------------------------


def test_uncovered_counts_lines_and_branches() -> None:
    diff = (_FX / "uncovered" / "diff.txt").read_text(encoding="utf-8")
    cov = json.loads((_FX / "uncovered" / "coverage.json").read_text(encoding="utf-8"))
    result = bc.uncovered(bc.parse_diff_added(diff), cov)
    assert result["n_touched"] == 10  # 8 lines + 2 branches
    assert result["n_uncovered"] == 4  # lines 13, 24, 25 and branch 12->13
    kinds = sorted((i["file"], i["line"], i["kind"]) for i in result["items"])
    assert kinds == [("src/tasks.py", 12, "branch"), ("src/tasks.py", 13, "line"),
                     ("src/tasks.py", 24, "line"), ("src/tasks.py", 25, "line")]
    assert result["provisional"] is True


def test_parse_diff_added_lines() -> None:
    added = bc.parse_diff_added((_FX / "uncovered" / "diff.txt").read_text(encoding="utf-8"))
    assert added["src/tasks.py"] == {11, 12, 13, 14, 24, 25}
    assert added["src/new.py"] == {1, 2}
    assert added["README.md"] == {2}


# ---------------------------------------------------------------------------
# ITF-017 baseline
# ---------------------------------------------------------------------------


def test_baseline_state() -> None:
    before = (_FX / "baseline" / "before.json").read_bytes()
    moved = (_FX / "baseline" / "moved.json").read_bytes()
    same = bc.baseline_state(before, before)
    assert same["moved"] is False and same["sha_before"] == same["sha_after"]
    changed = bc.baseline_state(before, moved)
    assert changed["moved"] is True and changed["sha_before"] != changed["sha_after"]
    assert bc.baseline_state(None, None, known=False)["moved"] is None


# ---------------------------------------------------------------------------
# ITF-010 crap
# ---------------------------------------------------------------------------

_QG = Path(__file__).resolve().parent / "fixtures" / "quality_gate"


def test_crap_above_target() -> None:
    radon = json.loads((_QG / "radon.json").read_text(encoding="utf-8"))
    cov = json.loads((_QG / "coverage.json").read_text(encoding="utf-8"))
    found = bc.crap_findings(radon, cov, ["src/pkg/mod.py"], target=8)
    assert [f["key"] for f in found] == ["src/pkg/mod.py::decorated", "src/pkg/mod.py::fresh"]
    assert found[0]["crap"] == 30.0 and found[0]["cc"] == 5
    assert bc.crap_findings(radon, cov, ["src/other.py"], target=8) == []


def test_crap_target_below_floor() -> None:
    with pytest.raises(ValueError):
        bc.crap_findings({}, {}, [], target=5)
    assert bc.main(["crap", "--radon", str(_QG / "radon.json"), "--coverage", str(_QG / "coverage.json"),
                    "--files", "src/pkg/mod.py", "--target", "5"]) == 2


# ---------------------------------------------------------------------------
# ITF-015 record, ITF-020 status
# ---------------------------------------------------------------------------


def _gate_unknown() -> dict:
    return json.loads((_FX / "gate" / "gate-json-with-unknown.json").read_text(encoding="utf-8"))


def test_record_keeps_unknown_keys_and_contract() -> None:
    payload = {"step": {"mode": "test-first", "status": "PASS"}, "scenarios": {K3: {"red": {"reason_ok": True}}},
               "fast": {"exit_code": 0, "status": "PASS", "ref": "_output/quality/x.json"}}
    out = bc.record(_gate_unknown(), 2, payload, at="2026-10-06T18:00:00Z", plan="plan-000123")
    assert out["x_extra"] == {"keep": True}
    assert out["schema_version"] == 1 and out["full"] is None and out["ts"] == "2026-10-06T18:00:00Z"
    assert out["fast"] == {"exit_code": 0, "category": "PASS", "ref": "_output/quality/x.json"}
    assert out["build"]["steps"]["2"]["status"] == "PASS"
    assert out["build"]["scenarios"][K3]["red"]["reason_ok"] is True
    assert out["build"]["scenarios"][K3]["step"] == 2
    assert out["build"]["plan"] == "plan-000123"


def test_record_category_names_and_baseline() -> None:
    out = bc.record({}, 1, {"fast": {"exit_code": 4, "status": "FAIL", "ref": "r"}}, at="t")
    assert out["fast"]["category"] == "CRAP"
    out = bc.record({}, 0, {"full": {"exit_code": 0, "status": "PASS", "ref": "r"}, "baseline_moved": True}, at="t")
    assert out["full"]["category"] == "PASS_WITH_BASELINE"
    assert out["baseline_moved"] is True


def test_record_is_idempotent(tmp_path: Path) -> None:
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps({"step": {"mode": "test-first", "status": "PASS"}}), encoding="utf-8")
    args = ["record", "--root", str(tmp_path), "--feature", "task-list", "--step", "1", "--from", str(payload),
            "--at", "2026-10-06T18:00:00Z"]
    assert bc.main(args) == 0
    first = (tmp_path / "features" / "task-list" / "gate.json").read_bytes()
    assert bc.main(args) == 0
    assert (tmp_path / "features" / "task-list" / "gate.json").read_bytes() == first


def test_status_next_phase() -> None:
    gate = {"build": {"steps": {"2": {"mode": "test-first", "phases": {"red": {"ok": True, "tries": 1}}}}}}
    assert bc.next_phase(gate, 2) == "GREEN"
    assert bc.next_phase({}, 2) == "RED"
    gate["build"]["steps"]["2"]["phases"]["green"] = {"ok": True, "tries": 1}
    assert bc.next_phase(gate, 2) == "REC"
    assert bc.next_phase(gate, 2, pipeline=True) == "CLEAN"
    gate["build"]["steps"]["2"]["status"] = "PASS"
    assert bc.next_phase(gate, 2) == "DONE"


# ---------------------------------------------------------------------------
# ITF-001, ITF-003, ITF-021 route (golden of the v1 plans)
# ---------------------------------------------------------------------------

_LEGACY = ["implement", "write-tests", "verify", "gate-fast", "note", "commit"]
_TDD = ["test-red", "implement-green", "verify", "gate-fast", "note", "commit"]


def test_v1_fixtures_unchanged() -> None:
    hashes = json.loads((_FX / "plans" / "v1-hashes.json").read_text(encoding="utf-8"))
    for name, digest in hashes.items():
        assert hashlib.sha256((_PF / name).read_bytes()).hexdigest() == digest


def test_route_v1_with_tests_golden() -> None:
    route = bc.route((_PF / "v1-plan-with-tests.md").read_text(encoding="utf-8"))
    assert route["version"] == 1 and route["refusal"] is None
    assert route["preamble"] == ["version-check"]
    assert [s["mode"] for s in route["steps"]] == ["legacy", "tdd", "legacy", "tdd", "legacy"]
    assert route["steps"][0]["actions"] == _LEGACY and route["steps"][1]["actions"] == _TDD
    assert route["end"] == ["quality-gate", "done"]


def test_route_v1_doc_only_golden() -> None:
    route = bc.route((_PF / "v1-plan-doc-only.md").read_text(encoding="utf-8"))
    assert [s["mode"] for s in route["steps"]] == ["legacy"] * 7
    assert all(s["actions"] == _LEGACY for s in route["steps"])


def test_route_pipeline_refused_on_v1() -> None:
    route = bc.route((_PF / "v1-plan-with-tests.md").read_text(encoding="utf-8"), pipeline=True)
    assert route["refusal"] == "`--pipeline` é do plano v2; este plano roda como antes."
    assert route["steps"] == []
    assert bc.main(["route", str(_PF / "v1-plan-with-tests.md"), "--pipeline"]) == 1


def test_route_v2_classes() -> None:
    route = bc.route((_PS / "v2-completo" / "plan.md").read_text(encoding="utf-8"))
    assert route["preamble"] == ["version-check", "check-plan-scenarios", "check-specify-status"]
    modes = [s["mode"] for s in route["steps"]]
    assert modes == ["no-scenario", "test-first", "test-first", "test-first", "no-scenario"]
    first = route["steps"][1]["actions"]
    assert first[:4] == ["pre", "red", "red-check", "freeze"]
    assert "clean" not in first and "hard" not in first
    assert route["steps"][0]["reason"].startswith("tabela usada")
    assert route["end"][0] == "full"


def test_route_v2_pipeline_adds_clean_and_hard() -> None:
    route = bc.route((_PS / "v2-completo" / "plan.md").read_text(encoding="utf-8"), pipeline=True)
    actions = route["steps"][1]["actions"]
    assert actions.index("clean") < actions.index("hard") < actions.index("record")


def test_route_unknown_version() -> None:
    route = bc.route("# Plan\nplan_format_version: 3\n\n## Steps\n")
    assert route["refusal"] == "plan_format_version 3 não suportada"


def test_route_absent_version_falls_back_to_manual() -> None:
    route = bc.route("# Plan\n\n## Steps\n\n### Step 1: x\n- **Tests**: N/A (doc)\n")
    assert route["fallback"] == "manual"


# ---------------------------------------------------------------------------
# ITF-023 export, ITF-024 demo
# ---------------------------------------------------------------------------


def _built_gate() -> dict:
    gate = bc.record({}, 2, {"step": {"mode": "test-first", "status": "PASS"},
                             "scenarios": {K3: {"red": {"reason_ok": True}, "final": {"test_result": "passed"}},
                                           K1: {"final": {"test_result": "passed"}}}}, at="t")
    return bc.record(gate, 0, {"feature": {"touched_total": 10, "touched_uncovered": 4, "base": "abc", "baseline_moved": False}}, at="t")


def test_export_writes_the_drift_files() -> None:
    files = bc.export_files(_built_gate(), "task-list", cucumber=[{"uri": "x"}])
    assert json.loads(files["features/task-list/drift/red-reason.json"]) == {"schema_version": 1, "scenarios": {K3: True}}
    assert json.loads(files["features/task-list/drift/coverage.json"]) == {
        "schema_version": 1, "base": "abc", "touched_total": 10, "touched_uncovered": 4}
    assert json.loads(files["features/task-list/runner/cucumber.json"]) == [{"uri": "x"}]
    assert json.loads(files["features/task-list/gate.json"])["baseline_moved"] is False


def test_demo_is_the_citizen_register() -> None:
    steps = {K3: ["Dado que a lista tem a tarefa pendente \"tarefa de compras\"",
                  "Quando eu marco a tarefa \"tarefa de compras\" como feita",
                  "Então a lista mostra a tarefa \"tarefa de compras\" como feita"],
             K1: ["Dado que a lista de tarefas está vazia"],
             K2: ["Dado que a lista de tarefas está vazia"]}
    questions = ["Se a tarefa marcada continuasse pendente, nenhum cenário perceberia. Isso importa para você?"]
    text = bc.demo_text(_built_gate(), steps, questions)
    assert "demonstrado" in text and "não medido" in text and "Isso importa para você?" in text
    stripped = text
    for lines in steps.values():
        for line in lines:
            stripped = stripped.replace(line, "")
    assert "PASS" not in stripped and "%" not in stripped
    assert not any(ch.isdigit() for ch in stripped)


# ---------------------------------------------------------------------------
# ITF-016 install-plugin
# ---------------------------------------------------------------------------


def test_install_plugin_is_idempotent(tmp_path: Path) -> None:
    assert bc.main(["install-plugin", str(tmp_path)]) == 0
    plugin = tmp_path / "tests" / "scenario_report.py"
    conftest = tmp_path / "tests" / "conftest.py"
    assert plugin.is_file() and 'pytest_plugins = ["scenario_report"]' in conftest.read_text(encoding="utf-8")
    first = (plugin.read_bytes(), conftest.read_bytes())
    assert bc.main(["install-plugin", str(tmp_path)]) == 0
    assert (plugin.read_bytes(), conftest.read_bytes()) == first


def test_install_plugin_refuses_a_hand_edited_copy(tmp_path: Path) -> None:
    assert bc.main(["install-plugin", str(tmp_path)]) == 0
    plugin = tmp_path / "tests" / "scenario_report.py"
    plugin.write_text(plugin.read_text(encoding="utf-8") + "\n# editado\n", encoding="utf-8")
    assert bc.main(["install-plugin", str(tmp_path)]) == 1
    assert plugin.read_text(encoding="utf-8").endswith("# editado\n")

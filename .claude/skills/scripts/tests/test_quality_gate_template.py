"""Tests for the quality-gate template core (gate.py, stdlib only)."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = ROOT / ".claude/references/template/quality-gate/python/gate.py"
FIX = Path(__file__).parent / "fixtures" / "quality_gate"


def _load():
    spec = importlib.util.spec_from_file_location("quality_gate_template", GATE_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gate = _load()
MOD = "src/pkg/mod.py"


@pytest.fixture
def metrics():
    radon = json.loads((FIX / "radon.json").read_text())
    cov = json.loads((FIX / "coverage.json").read_text())
    return gate.join_metrics(radon, cov, ".")


def key(q):
    return "%s::%s" % (MOD, q)


def test_crap_values():
    assert gate.crap(5, 0.0) == 30.0
    assert gate.crap(26, 0.92) == pytest.approx(26.35, abs=0.01)
    assert gate.crap(4, 1.0) == 4.0


def test_join_keys_and_class_ignored(metrics):
    assert key("K") not in metrics
    assert key("K.meth") in metrics
    assert key("K.meth.inner") in metrics
    assert key("plain") in metrics


def test_join_coverage_formula(metrics):
    assert metrics[key("plain")].cov == 1.0
    assert metrics[key("K.meth")].cov == pytest.approx(0.5)
    assert metrics[key("K.meth.inner")].cov == 1.0  # no statements


def test_decorated_unexecuted_body_is_zero(metrics):
    m = metrics[key("decorated")]
    assert m.cov == 0.0
    assert m.crap == 30.0


def test_join_miss_finding():
    radon = {"a.py": [{"type": "function", "name": "f", "lineno": 1, "endline": 2,
                       "complexity": 1, "closures": []}]}
    ms = gate.join_metrics(radon, {"files": {}}, ".")
    assert ms["a.py::f"].cov == 0.0
    f = gate.join_findings(ms)
    assert f and f[0].category == 1 and f[0].key == "join-miss"
    assert gate.exit_code(f) == 1


def test_new_function_crap_11_is_finding(metrics):
    f = gate.evaluate_crap({key("fresh"): metrics[key("fresh")]}, {"functions": {}}, set(), 10, 30)
    assert metrics[key("fresh")].crap == pytest.approx(11 * 11 + 11)  # cov 0, cc 11 -> 132
    assert f and f[0].category == 4 and f[0].key == key("fresh")


def _m(crap_value, name="f"):
    return {"a.py::" + name: gate.FunctionMetric("a.py", name, 1, 5, 5, 0.5, crap_value)}


def test_touched_over_limit():
    ms = _m(11.0)
    base = {"functions": {"a.py::f": {"crap": 11.0}}}
    f = gate.evaluate_crap(ms, base, {"a.py::f"}, 10, 30)
    assert [x.category for x in f] == [4]


def test_untouched_rise_over_baseline():
    base = {"functions": {"a.py::f": {"crap": 12.0}}}
    assert gate.evaluate_crap(_m(13.0), base, set(), 10, 30)
    assert gate.evaluate_crap(_m(12.0), base, set(), 10, 30) == []


def test_legacy_over_ceiling_is_warning_only():
    base = {"functions": {"a.py::f": {"crap": 40.0}}}
    f = gate.evaluate_crap(_m(40.0), base, set(), 10, 30)
    assert len(f) == 1 and f[0].severity == "warning"
    assert gate.exit_code(f) == 0


def test_baseline_25_to_31_is_finding():
    base = {"functions": {"a.py::f": {"crap": 25.0}}}
    f = gate.evaluate_crap(_m(31.0), base, set(), 10, 30)
    assert f and f[0].category == 4 and f[0].severity == "error"


def test_ratchet_markers():
    now = {"xfail": {"total": 1, "unjustified": 1}}
    f = gate.ratchet_markers(now, {})
    assert f and f[0].category == 7
    ok = {"xfail": {"total": 1, "unjustified": 0}}
    assert gate.ratchet_markers(ok, {}) == []


def test_exit_code():
    f4 = gate.Finding(4, "k", "m")
    f6 = gate.Finding(6, "k", "m")
    f1 = gate.Finding(1, "k", "m")
    assert gate.exit_code([f6, f4]) == 4
    assert gate.exit_code([]) == 0
    assert gate.exit_code([f4, f1]) == 1


def _diff(path, hunk):
    return "--- a/%s\n+++ b/%s\n%s\n" % (path, path, hunk)


def test_touched_added_lines(metrics):
    t = gate.touched_functions(_diff(MOD, "@@ -3,0 +4,2 @@"), [], metrics)
    assert t == {key("plain")}


def test_touched_inside_method_and_closure(metrics):
    t = gate.touched_functions(_diff(MOD, "@@ -31 +31 @@"), [], metrics)
    assert key("K.meth") in t and key("K.meth.inner") in t
    assert key("plain") not in t


def test_touched_removal_hunk(metrics):
    t = gate.touched_functions(_diff(MOD, "@@ -26,3 +25,0 @@"), [], metrics)
    assert t == {key("K.meth")}


def test_touched_untracked_file(metrics):
    t = gate.touched_functions("", [MOD], metrics)
    assert key("fresh") in t and key("plain") in t


def test_deleted_file_ignored(metrics):
    d = "--- a/%s\n+++ /dev/null\n@@ -1,5 +0,0 @@\n" % MOD
    assert gate.touched_functions(d, [], metrics) == set()


def test_core_has_no_harness_imports():
    text = GATE_PATH.read_text()
    assert "project_config" not in text and "check_" not in text
    assert text.isascii()

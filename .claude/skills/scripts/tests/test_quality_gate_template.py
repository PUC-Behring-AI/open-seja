"""Tests for the quality-gate template core (gate.py, stdlib only)."""
import datetime
import importlib.util
import json
import os
import subprocess
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


# --------------------------------------------------------------------------
# Executor (Step 3): run() is injected, no external tool is needed.
# --------------------------------------------------------------------------
RADON_OK = {"src/pkg/mod.py": [
    {"type": "function", "name": "plain", "lineno": 1, "endline": 10,
     "col_offset": 0, "complexity": 2, "closures": []}]}
COV_FN = {"summary": {"covered_lines": 8, "num_statements": 8,
                      "covered_branches": 2, "num_branches": 2}}


def _cov_json(ts=None):
    ts = ts or datetime.datetime.now().isoformat()
    return {"meta": {"timestamp": ts},
            "files": {"src/pkg/mod.py": {"functions": {"plain": COV_FN}}}}


class Stub:
    """Injectable run(cmd, env, cwd, timeout)."""

    def __init__(self, cwd, codes=None, write_cov=True, cov_ts=None, outputs=None):
        self.cwd = Path(cwd)
        self.codes = codes or {}
        self.write_cov = write_cov
        self.cov_ts = cov_ts
        self.outputs = outputs or {}
        self.calls = []

    def __call__(self, cmd, env, cwd, timeout):
        self.calls.append((list(cmd), dict(env)))
        head = cmd[0]
        if head == "git" and "merge-base" in cmd:
            return gate.RunResult(self.codes.get("merge-base", 0), "abc123\n", "")
        if head == "git":
            return gate.RunResult(0, self.outputs.get("git", ""), "")
        if head == "pytest" and self.write_cov:
            (self.cwd / "coverage.json").write_text(json.dumps(_cov_json(self.cov_ts)))
        if head == "radon":
            return gate.RunResult(0, json.dumps(RADON_OK), "")
        if head == "mutmut" and cmd[1] == "results":
            return gate.RunResult(0, self.outputs.get("mutmut", ""), "")
        return gate.RunResult(self.codes.get(head, 0), self.outputs.get(head, ""), "")

    def names(self):
        return [c[0][0] for c in self.calls]

    def env_of(self, head):
        return [e for c, e in self.calls if c[0] == head][0]


def _project(tmp_path, tests="def test_a():\n    assert 1 == 1\n", extra_toml=""):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "pkg"\n[tool.seja-gate]\n' + extra_toml)
    (tmp_path / "src/pkg").mkdir(parents=True)
    (tmp_path / "src/pkg/__init__.py").write_text("")
    (tmp_path / "src/pkg/mod.py").write_text("def plain():\n    return 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_mod.py").write_text(tests)
    base = {"version": 1, "functions": {
        "src/pkg/mod.py::plain": {"cc": 2, "cov": 1.0, "crap": 2.0, "survived": 0}},
        "markers": {}, "mutation": {"survived_total": 0}}
    (tmp_path / "quality-baseline.json").write_text(json.dumps(base))
    return tmp_path


def _run(tmp_path, args, stub, env=None):
    out = tmp_path / "out"
    code = gate.main(list(args) + ["--out-dir", str(out)], run=stub,
                     which=lambda name: "/bin/" + name, cwd=str(tmp_path),
                     env=env if env is not None else {})
    return code, out


def test_ruff_failure_exits_2_and_skips_pytest(tmp_path):
    p = _project(tmp_path)
    stub = Stub(p, codes={"ruff": 1})
    code, _ = _run(p, ["--fast"], stub)
    assert code == 2
    assert "pytest" not in stub.names()


def test_all_stages_pass_writes_json(tmp_path, capsys):
    p = _project(tmp_path)
    stub = Stub(p)
    code, out = _run(p, ["--fast", "--json"], stub)
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["version"] == 1 and payload["status"] == "PASS"
    assert payload["level"] == "fast" and payload["exit_code"] == 0
    assert {s["name"] for s in payload["stages"]} >= {"ruff", "pyright", "pytest", "crap"}
    assert len(list(out.glob("gate-*.json"))) == 1


def test_stage_order(tmp_path):
    p = _project(tmp_path)
    stub = Stub(p)
    _run(p, ["--fast"], stub)
    names = stub.names()
    assert names.index("ruff") < names.index("pyright") < names.index("pytest") < names.index("radon")


def test_pytest_env_scrubbed(tmp_path):
    p = _project(tmp_path)
    stub = Stub(p)
    env = {"ANTHROPIC_API_KEY": "k", "ANTHROPIC_AUTH_TOKEN": "t",
           "CLAUDE_CODE_OAUTH_TOKEN": "o", "FOO_TOKEN": "x", "MY_SECRET": "s",
           "PATH": "/usr/bin"}
    _run(p, ["--fast"], stub, env=env)
    e = stub.env_of("pytest")
    assert e == {"PATH": "/usr/bin"}


def test_env_passthrough_respected(tmp_path):
    p = _project(tmp_path, extra_toml='env_passthrough = ["FOO_TOKEN"]\n')
    stub = Stub(p)
    _run(p, ["--fast"], stub, env={"FOO_TOKEN": "x", "BAR_TOKEN": "y"})
    e = stub.env_of("pytest")
    assert e.get("FOO_TOKEN") == "x" and "BAR_TOKEN" not in e


def test_stale_coverage(tmp_path, capsys):
    p = _project(tmp_path)
    stub = Stub(p, write_cov=False)
    (p / "coverage.json").write_text(json.dumps(_cov_json("2000-01-01T00:00:00")))
    code, _ = _run(p, ["--fast", "--json"], stub)
    payload = json.loads(capsys.readouterr().out)
    assert code == 1 and payload["status"] == "ERROR"
    assert any(f["key"] == "stale-coverage" for f in payload["findings"])


def test_accept_baseline_requires_yes(tmp_path):
    p = _project(tmp_path)
    before = (p / "quality-baseline.json").read_text()
    code, _ = _run(p, ["--accept-baseline"], Stub(p))
    assert code == 1
    assert (p / "quality-baseline.json").read_text() == before


def test_accept_baseline_with_yes_overwrites(tmp_path):
    p = _project(tmp_path)
    (p / "quality-baseline.json").write_text("{}")
    code, _ = _run(p, ["--accept-baseline", "--yes"], Stub(p))
    assert code == 0
    data = json.loads((p / "quality-baseline.json").read_text())
    assert data["version"] == 1 and "src/pkg/mod.py::plain" in data["functions"]


def test_init_baseline_only_if_absent(tmp_path):
    p = _project(tmp_path)
    (p / "quality-baseline.json").write_text('{"keep": true}')
    code, _ = _run(p, ["--init-baseline"], Stub(p))
    assert code == 0
    assert json.loads((p / "quality-baseline.json").read_text()) == {"keep": True}
    (p / "quality-baseline.json").unlink()
    code, _ = _run(p, ["--init-baseline"], Stub(p))
    assert code == 0 and (p / "quality-baseline.json").exists()


def test_accept_abbreviation_rejected(tmp_path):
    p = _project(tmp_path)
    with pytest.raises(SystemExit) as exc:
        gate.main(["--accept-b", "--yes"], run=Stub(p), which=lambda n: n, cwd=str(p), env={})
    assert exc.value.code == 2


def test_test_without_assert_exits_3(tmp_path, capsys):
    p = _project(tmp_path, tests="def test_noassert():\n    x = 1\n\ndef test_ok():\n    assert True\n")
    stub = Stub(p)
    code, _ = _run(p, ["--fast", "--json"], stub)
    payload = json.loads(capsys.readouterr().out)
    assert code == 3
    assert any("test_noassert" in f["key"] for f in payload["findings"])
    assert "pytest" not in stub.names()


def test_test_with_raises_is_ok(tmp_path):
    p = _project(tmp_path, tests=(
        "import pytest\n\ndef test_r():\n    with pytest.raises(ValueError):\n        int('x')\n"))
    code, _ = _run(p, ["--fast"], Stub(p))
    assert code == 0


def test_missing_tool_lists_suggestion(tmp_path, capsys):
    p = _project(tmp_path)
    code = gate.main(["--fast", "--json", "--out-dir", str(p / "o")], run=Stub(p),
                     which=lambda n: None if n == "radon" else "/bin/" + n,
                     cwd=str(p), env={})
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    msg = " ".join(f["message"] for f in payload["findings"])
    assert "radon" in msg and "uv add --dev" in msg


def test_no_diff_base(tmp_path, capsys):
    p = _project(tmp_path)
    code, _ = _run(p, ["--fast", "--json"], Stub(p, codes={"merge-base": 1}))
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert any(f["key"] == "no-diff-base" for f in payload["findings"])


def test_touched_function_over_limit_exits_4(tmp_path):
    p = _project(tmp_path, extra_toml="crap_max_touched = 1\n")
    diff = "+++ b/src/pkg/mod.py\n@@ -1,0 +1,1 @@\n+x\n"
    code, _ = _run(p, ["--fast"], Stub(p, outputs={"git": diff}))
    assert code == 4


def test_no_pyproject_is_error(tmp_path):
    env = dict(os.environ)
    res = subprocess.run([sys.executable, str(GATE_PATH), "--json"], cwd=str(tmp_path),
                         capture_output=True, text=True, env=env)
    assert res.returncode == 1
    assert json.loads(res.stdout)["status"] == "ERROR"


def test_help_lists_options():
    res = subprocess.run([sys.executable, str(GATE_PATH), "--help"], capture_output=True, text=True)
    for opt in ("--fast", "--full", "--files", "--json", "--init-baseline",
                "--accept-baseline", "--yes", "--out-dir"):
        assert opt in res.stdout


def test_out_dir_from_env(tmp_path):
    p = _project(tmp_path)
    qdir = tmp_path / "qd"
    code = gate.main(["--fast"], run=Stub(p), which=lambda n: n, cwd=str(p),
                     env={"SEJA_QUALITY_DIR": str(qdir)})
    assert code == 0 and list(qdir.glob("gate-*.json"))


# ---- mutation ------------------------------------------------------------

def test_mutant_to_key_function_and_method():
    files = ["src/pkg/mod.py"]
    assert gate.mutant_to_key("pkg.mod.x_plain__mutmut_2", files) == "src/pkg/mod.py::plain"
    assert gate.mutant_to_key("pkg.mod.x\u01c1K\u01c1meth__mutmut_3", files) == "src/pkg/mod.py::K.meth"
    assert gate.mutant_to_key("other.mod.x_f__mutmut_1", files) is None


def test_parse_mutmut_results_fixture():
    text = (FIX / "mutmut_results.txt").read_text(encoding="utf-8")
    rows = gate.parse_mutmut_results(text)
    assert ("pkg.mod.x\u01c1K\u01c1meth__mutmut_3", "survived") in rows
    assert len(rows) == 4


def test_mutation_globs():
    metrics = {}
    for k in ("src/pkg/mod.py::plain", "src/pkg/mod.py::K.meth"):
        f, q = k.split("::")
        metrics[k] = gate.FunctionMetric(f, q, 1, 2, 1, 1.0, 1.0)
    globs = gate.mutation_globs(list(metrics), ["src/"])
    assert "pkg.mod.x_plain__mutmut_*" in globs
    assert "pkg.mod.x\u01c1K\u01c1meth__mutmut_*" in globs


def test_files_option_limits_globs(tmp_path):
    p = _project(tmp_path)
    stub = Stub(p, outputs={"mutmut": ""})
    code, _ = _run(p, ["--full", "--files", "src/pkg/mod.py"], stub)
    runs = [c for c, _e in stub.calls if c[0] == "mutmut" and c[1] == "run"]
    assert runs and "pkg.mod.x_plain__mutmut_*" in runs[0]


def test_full_survivor_in_target_exits_6_and_mutmut_env_scrubbed(tmp_path):
    p = _project(tmp_path)
    out = "    pkg.mod.x_plain__mutmut_2: survived\n"
    stub = Stub(p, outputs={"mutmut": out})
    code, _ = _run(p, ["--full", "--files", "src/pkg/mod.py"], stub,
                   env={"ANTHROPIC_API_KEY": "k"})
    assert code == 6
    assert "ANTHROPIC_API_KEY" not in stub.env_of("mutmut")


def test_marker_ratchet_exits_7(tmp_path):
    p = _project(tmp_path)
    (p / "src/pkg/mod.py").write_text(
        "def plain():\n    return 1  # pragma: no cover\n")
    code, _ = _run(p, ["--fast"], Stub(p))
    assert code == 7


def test_pytest_cmd_does_not_register_timeout_plugin_twice(tmp_path):
    p = _project(tmp_path)
    stub = Stub(p)
    _run(p, ["--fast"], stub)
    cmd = [c for c, _ in stub.calls if c[0] == "pytest"][0]
    assert "-p" not in cmd and "--timeout=30" in cmd


def test_missing_pytest_timeout_plugin_is_config_error(tmp_path):
    p = _project(tmp_path)
    stub = Stub(p, codes={"pytest": 4},
                outputs={"pytest": "pytest: error: unrecognized arguments: --timeout=30"})
    code, _ = _run(p, ["--fast"], stub)
    assert code == 1


def test_crap_message_has_cc_cov_and_hint():
    hi = {"a.py::f": gate.FunctionMetric("a.py", "f", 1, 5, 13, 1.0, 13.0)}
    msg = gate.evaluate_crap(hi, {"functions": {}}, set(), 10, 30)[0].message
    assert "cc=13" in msg and "cov=100%" in msg and "reduce complexity" in msg
    lo = {"a.py::f": gate.FunctionMetric("a.py", "f", 1, 5, 5, 0.0, 30.0)}
    msg = gate.evaluate_crap(lo, {"functions": {}}, set(), 10, 30)[0].message
    assert "cc=5" in msg and "cov=0%" in msg and "add tests" in msg


def test_example_toml_excludes_gate_and_hooks():
    here = Path(gate.__file__).parent
    text = (here / "pyproject-dev.example.toml").read_text()
    assert "extend-exclude" in text and "gate.py" in text and ".claude" in text
    assert "[tool.pyright]" in text

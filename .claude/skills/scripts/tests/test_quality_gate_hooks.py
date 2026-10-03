"""Tests for the quality-gate hooks (.claude/hooks/quality_gate_*.py)."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS_DIR = Path(__file__).resolve().parents[2].parent / "hooks"
SCRIPTS_DIR = Path(__file__).resolve().parents[1]

STUB = '''\
import json, os, sys, time
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "calls.log"), "a") as fh:
    fh.write(json.dumps(sys.argv[1:]) + "\\n")
if os.path.exists(os.path.join(here, "sleep")):
    time.sleep(30)
resp = open(os.path.join(here, "response.txt")).read()
sys.stdout.write(resp)
sys.exit(int(open(os.path.join(here, "exit.txt")).read()))
'''


def _load(name):
    sys.path.insert(0, str(HOOKS_DIR))
    try:
        spec = importlib.util.spec_from_file_location(name, HOOKS_DIR / (name + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(str(HOOKS_DIR))
    return mod


@pytest.fixture
def stop():
    return _load("quality_gate_stop")


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _report(status, code, findings=()):
    return json.dumps({"version": 1, "level": "fast", "status": status,
                       "exit_code": code, "findings": list(findings)})


class Repo:
    def __init__(self, root):
        self.root = root
        self.stub_dir = root.parent / (root.name + "-stub")
        self.stub_dir.mkdir()
        (self.stub_dir / "stub_gate.py").write_text(STUB)
        self.tmp = root.parent / (root.name + "-tmp")
        self.tmp.mkdir()
        self.set_gate(_report("PASS", 0), 0)

    def set_gate(self, response, code):
        (self.stub_dir / "response.txt").write_text(response)
        (self.stub_dir / "exit.txt").write_text(str(code))

    def stub_cmd(self):
        return "%s %s --json" % (sys.executable, self.stub_dir / "stub_gate.py")

    def write_conventions(self, fast_cmd=None, output_dir="_output", commit_cmd=""):
        if fast_cmd is None:
            fast_cmd = self.stub_cmd()
        (self.root / "product-design").mkdir(exist_ok=True)
        (self.root / "product-design" / "conventions.md").write_text(
            "| Variable | Value | Description |\n|---|---|---|\n"
            "| `OUTPUT_DIR` | `%s` | out |\n"
            "| `QUALITY_DIR` | `${OUTPUT_DIR}/quality` | q |\n"
            "| `GATE_FAST_CMD` | `%s` | fast |\n"
            "| `GATE_COMMIT_CMD` | `%s` | commit |\n" % (output_dir, fast_cmd, commit_cmd))

    def calls(self):
        log = self.stub_dir / "calls.log"
        if not log.exists():
            return []
        return [json.loads(line) for line in log.read_text().splitlines()]

    @property
    def env(self):
        return {"CLAUDE_PROJECT_DIR": str(self.root), "TMPDIR": str(self.tmp)}


@pytest.fixture
def git_repo(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    (root / "a.py").write_text("x = 1\n")
    (root / "b.py").write_text("y = 1\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "init")
    repo = Repo(root)
    repo.write_conventions()
    return repo


def payload(active=False, sid="s1"):
    return {"session_id": sid, "stop_hook_active": active}


def dirty(repo, name="a.py"):
    (repo.root / name).write_text("x = %d\n" % len(list(repo.root.iterdir())) + "z = 2\n")


FAIL_CRAP = _report("FAIL", 4, [{"category": 4, "key": "a.py::f", "message": "CRAP(a.py::f)=31 > 30"}])


def test_empty_gate_cmd_exits_zero_without_running(stop, git_repo):
    git_repo.write_conventions(fast_cmd="")
    dirty(git_repo)
    assert stop.main(payload(), git_repo.env) == (0, "")
    assert git_repo.calls() == []


def test_unfilled_placeholder_is_treated_as_empty(stop, git_repo):
    git_repo.write_conventions(fast_cmd="{{GATE_FAST_CMD}}")
    dirty(git_repo)
    assert stop.main(payload(), git_repo.env)[0] == 0
    assert git_repo.calls() == []


def test_no_modified_py_exits_zero(stop, git_repo):
    (git_repo.root / "notes.md").write_text("hi\n")
    assert stop.main(payload(), git_repo.env)[0] == 0
    assert git_repo.calls() == []


def test_fail_blocks_with_finding_key(stop, git_repo):
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo)
    code, err = stop.main(payload(), git_repo.env)
    assert code == 2
    assert err.startswith("Quality gate FAIL (exit 4):")
    assert "a.py::f" in err


def test_pass_exits_zero_and_passes_files(stop, git_repo):
    dirty(git_repo)
    assert stop.main(payload(), git_repo.env)[0] == 0
    (argv,) = git_repo.calls()
    assert argv[argv.index("--files"):] == ["--files", "a.py"]


def test_untracked_py_is_included(stop, git_repo):
    (git_repo.root / "new.py").write_text("z = 1\n")
    assert stop.main(payload(), git_repo.env)[0] == 0
    (argv,) = git_repo.calls()
    assert "new.py" in argv


def test_deleted_file_is_not_passed(stop, git_repo):
    (git_repo.root / "b.py").unlink()
    dirty(git_repo, "a.py")
    stop.main(payload(), git_repo.env)
    (argv,) = git_repo.calls()
    assert "b.py" not in argv and "a.py" in argv


def test_only_deleted_py_exits_zero(stop, git_repo):
    (git_repo.root / "b.py").unlink()
    assert stop.main(payload(), git_repo.env)[0] == 0
    assert git_repo.calls() == []


def test_repo_without_head_uses_untracked(stop, tmp_path):
    root = tmp_path / "fresh"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "n.py").write_text("a = 1\n")
    repo = Repo(root)
    repo.write_conventions()
    assert stop.main(payload(), repo.env)[0] == 0
    assert "n.py" in repo.calls()[0]


def test_error_status_blocks(stop, git_repo):
    git_repo.set_gate(_report("ERROR", 1, [{"category": 1, "key": "stale-coverage", "message": "old"}]), 1)
    dirty(git_repo)
    code, err = stop.main(payload(), git_repo.env)
    assert code == 2
    assert "Quality gate ERROR (exit 1):" in err and "stale-coverage" in err


def test_invalid_json_blocks(stop, git_repo):
    git_repo.set_gate("not json", 1)
    dirty(git_repo)
    code, err = stop.main(payload(), git_repo.env)
    assert code == 2
    assert "ERROR" in err and "version 1" in err


def test_pass_cache_skips_second_run(stop, git_repo):
    dirty(git_repo)
    assert stop.main(payload(), git_repo.env)[0] == 0
    assert stop.main(payload(), git_repo.env)[0] == 0
    assert len(git_repo.calls()) == 1
    (git_repo.root / "a.py").write_text("changed = 1\n")
    stop.main(payload(), git_repo.env)
    assert len(git_repo.calls()) == 2


def test_cache_does_not_hide_failures(stop, git_repo):
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo)
    assert stop.main(payload(), git_repo.env)[0] == 2
    assert stop.main(payload(True), git_repo.env)[0] == 2
    assert len(git_repo.calls()) == 2


def test_fourth_stop_releases_after_three_blocks(stop, git_repo):
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo)
    assert stop.main(payload(False), git_repo.env)[0] == 2
    assert stop.main(payload(True), git_repo.env)[0] == 2
    assert stop.main(payload(True), git_repo.env)[0] == 2
    code, err = stop.main(payload(True), git_repo.env)
    assert code == 0
    assert "released after 3 blocks; the human decides" in err
    assert len(git_repo.calls()) == 3
    # counter was reset: the next active stop blocks again
    assert stop.main(payload(True), git_repo.env)[0] == 2


def test_inactive_stop_resets_sequence(stop, git_repo):
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo)
    for active in (False, True, True):
        assert stop.main(payload(active), git_repo.env)[0] == 2
    assert stop.main(payload(False), git_repo.env)[0] == 2  # new turn, count restarts
    assert stop.main(payload(True), git_repo.env)[0] == 2
    assert stop.main(payload(True), git_repo.env)[0] == 2
    assert stop.main(payload(True), git_repo.env)[0] == 0


def test_sequences_are_per_session(stop, git_repo):
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo)
    for _ in range(3):
        stop.main(payload(True, "A"), git_repo.env)
    assert stop.main(payload(True, "B"), git_repo.env)[0] == 2
    state = git_repo.tmp / "seja-gate"
    assert sorted(p.name for p in state.iterdir()) == ["A.json", "B.json"]


def test_session_id_cannot_escape_state_dir(stop, git_repo):
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo)
    stop.main(payload(True, "../../evil"), git_repo.env)
    assert not (git_repo.tmp.parent / "evil.json").exists()
    assert all(p.parent == git_repo.tmp / "seja-gate" for p in (git_repo.tmp / "seja-gate").iterdir())


def test_timeout_blocks(stop, git_repo):
    (git_repo.stub_dir / "sleep").write_text("")
    dirty(git_repo)
    env = dict(git_repo.env, SEJA_GATE_HOOK_TIMEOUT="1")
    code, err = stop.main(payload(), env)
    assert code == 2
    assert "timeout" in err


def test_internal_exception_fails_open(stop, git_repo, monkeypatch):
    dirty(git_repo)

    def boom(*a, **k):
        raise RuntimeError("kaput")

    monkeypatch.setattr(stop.common, "run_gate", boom)
    code, err = stop.main(payload(), git_repo.env)
    assert code == 0
    assert "kaput" in err and "warning" in err.lower()


def test_conventions_with_output_dir_resolves_quality_dir(git_repo):
    common = _load("_gate_hook_common")
    git_repo.write_conventions(output_dir="out")
    conv = common.parse_conventions(git_repo.root)
    assert conv["QUALITY_DIR"] == "out/quality"


def test_parser_parity_with_project_config(git_repo, monkeypatch):
    common = _load("_gate_hook_common")
    monkeypatch.syspath_prepend(str(SCRIPTS_DIR))
    import project_config

    monkeypatch.setattr(project_config, "REPO_ROOT", git_repo.root)
    monkeypatch.setattr(project_config, "_config", None)
    mine = common.parse_conventions(git_repo.root)
    for key in ("OUTPUT_DIR", "QUALITY_DIR", "GATE_FAST_CMD"):
        assert mine[key] == project_config.get(key)


def test_parser_parity_on_real_template(monkeypatch):
    common = _load("_gate_hook_common")
    monkeypatch.syspath_prepend(str(SCRIPTS_DIR))
    import project_config

    repo_root = HOOKS_DIR.parents[1]
    template = repo_root / ".claude" / "references" / "template" / "conventions.md"
    text = template.read_text(encoding="utf-8")
    rows = common.parse_rows(text)
    assert rows == {m.group(1): m.group(2) for m in project_config._ROW_RE.finditer(text)}


def test_subprocess_blocks_with_exit_2(git_repo):
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo)
    import os

    env = dict(os.environ, **git_repo.env)
    env.pop("SEJA_GATE_HOOK_TIMEOUT", None)
    res = subprocess.run([sys.executable, str(HOOKS_DIR / "quality_gate_stop.py")],
                         input=json.dumps(payload()), text=True, capture_output=True,
                         env=env, cwd=str(git_repo.root), timeout=60)
    assert res.returncode == 2
    assert "a.py::f" in res.stderr


def test_subprocess_bad_stdin_fails_open(git_repo):
    import os

    env = dict(os.environ, **git_repo.env)
    res = subprocess.run([sys.executable, str(HOOKS_DIR / "quality_gate_stop.py")],
                         input="{not json", text=True, capture_output=True,
                         env=env, cwd=str(git_repo.root), timeout=60)
    assert res.returncode == 0
    assert "warning" in res.stderr.lower()


# ---------------------------------------------------------------- PreToolUse

@pytest.fixture
def pre():
    return _load("quality_gate_pretool")


def bash(pre, repo, command, extra_env=None):
    env = dict(repo.env, **(extra_env or {}))
    return pre.main({"tool_name": "Bash", "tool_input": {"command": command},
                     "cwd": str(repo.root)}, env)


def with_commit_gate(repo):
    repo.write_conventions(commit_cmd=repo.stub_cmd())


@pytest.mark.parametrize("cmd", [
    "uv run python gate.py --accept-baseline --yes",
    "python gate.py --accept-b --yes",
    "python gate.py --acc --yes",
    "cd x && python3 gate.py --accept-baseline",
])
def test_accept_baseline_always_blocked(pre, git_repo, cmd):
    code, err = bash(pre, git_repo, cmd)
    assert code == 2
    assert "only a human moves the quality baseline" in err


def test_accept_baseline_blocked_for_gate_command_from_conventions(pre, git_repo):
    git_repo.write_conventions(fast_cmd="mygate --json")
    assert bash(pre, git_repo, "mygate --accept-baseline")[0] == 2


def test_accept_prefix_in_unrelated_command_passes(pre, git_repo):
    assert bash(pre, git_repo, "grep --accept-baseline README.md")[0] == 0
    assert bash(pre, git_repo, "python other.py --acc")[0] == 0


@pytest.mark.parametrize("cmd", [
    "git commit --no-verify -m x",
    "git commit --no-verif -m x",
    "git commit --no-v -m x",
    "git commit -nm x",
    "git commit -anm x",
    "git commit -n -m x",
    "git -c user.name=a commit -n -m x",
    "git -c user.name=a commit -n",
    "git -C . --no-pager commit -n -m x",
    "FOO=1 git commit -n -m x",
    'bash -c "git commit -n -m x"',
    "sh -c 'git add -A && git commit --no-verify -m x'",
    "git -c core.hooksPath=/dev/null commit -m x",
    "git commit --config-env=core.hooksPath=H -m x",
    "git status; git commit -n",
    "git add . | cat\ngit commit -n",
])
def test_commit_hook_skips_blocked(pre, git_repo, cmd):
    code, err = bash(pre, git_repo, cmd.replace("\\n", "\n"))
    assert code == 2
    assert "commit hooks must not be skipped" in err


@pytest.mark.parametrize("cmd", [
    "git commit -mn",
    'git commit -m "fix -n flag"',
    "git commit -m 'x' -- -n",
    "git commit -am 'fix --no-verify'",
    "git commit -F msg.txt",
    "git status",
    "git log -n 3",
    "grep x README.md",
    "git commit --amend --no-edit",
])
def test_non_skipping_commands_pass_without_gate(pre, git_repo, cmd):
    assert bash(pre, git_repo, cmd) == (0, "")
    assert git_repo.calls() == []


def test_alias_resolved(pre, git_repo):
    _git(git_repo.root, "config", "alias.ci", "commit")
    assert bash(pre, git_repo, "git ci -n -m x")[0] == 2
    assert bash(pre, git_repo, "git ci -m x")[0] == 0


def test_commit_runs_commit_gate_on_union_and_blocks_on_fail(pre, git_repo):
    with_commit_gate(git_repo)
    git_repo.set_gate(FAIL_CRAP, 4)
    dirty(git_repo, "a.py")
    (git_repo.root / "new.py").write_text("q = 1\n")
    code, err = bash(pre, git_repo, "git add -A && git commit -m x")
    assert code == 2
    assert "a.py::f" in err
    argv = git_repo.calls()[-1]
    assert argv[-3:] == ["--files", "a.py", "new.py"]


def test_commit_gate_pass_exits_zero_and_no_cache(pre, git_repo):
    with_commit_gate(git_repo)
    dirty(git_repo)
    assert bash(pre, git_repo, "git commit -am x")[0] == 0
    assert bash(pre, git_repo, "git commit -am x")[0] == 0
    assert len(git_repo.calls()) == 2


def test_commit_gate_error_blocks(pre, git_repo):
    with_commit_gate(git_repo)
    git_repo.set_gate("not json", 1)
    dirty(git_repo)
    assert bash(pre, git_repo, "git commit -m x")[0] == 2


def test_commit_gate_timeout_blocks(pre, git_repo):
    with_commit_gate(git_repo)
    (git_repo.stub_dir / "sleep").write_text("1")
    dirty(git_repo)
    code, err = bash(pre, git_repo, "git commit -m x", {"SEJA_GATE_HOOK_TIMEOUT": "1"})
    assert code == 2
    assert "timeout" in err


def test_commit_without_py_changes_skips_gate(pre, git_repo):
    with_commit_gate(git_repo)
    (git_repo.root / "n.md").write_text("x")
    assert bash(pre, git_repo, "git add -A && git commit -m x")[0] == 0
    assert git_repo.calls() == []


def test_commit_blocked_when_gate_lines_changed(pre, git_repo):
    _git(git_repo.root, "add", "-A")
    _git(git_repo.root, "commit", "-q", "-m", "conv")
    conv = git_repo.root / "product-design" / "conventions.md"
    conv.write_text(conv.read_text().replace("GATE_FAST_CMD` | `", "GATE_FAST_CMD` | `true; "))
    code, err = bash(pre, git_repo, "git commit -am x")
    assert code == 2
    assert "gate config must be committed by a human" in err


def test_commit_allowed_when_other_conventions_lines_changed(pre, git_repo):
    _git(git_repo.root, "add", "-A")
    _git(git_repo.root, "commit", "-q", "-m", "conv")
    conv = git_repo.root / "product-design" / "conventions.md"
    conv.write_text(conv.read_text().replace("| out |", "| other |"))
    assert bash(pre, git_repo, "git commit -am x")[0] == 0


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit"])
def test_edit_tools_blocked_on_baseline(pre, git_repo, tool):
    code, err = pre.main({"tool_name": tool, "cwd": str(git_repo.root),
                          "tool_input": {"file_path": str(git_repo.root / "_output/quality/quality-baseline.json")}},
                         git_repo.env)
    assert code == 2
    assert "only a human moves the quality baseline" in err


def test_edit_on_other_file_passes(pre, git_repo):
    assert pre.main({"tool_name": "Edit", "cwd": str(git_repo.root),
                     "tool_input": {"file_path": str(git_repo.root / "a.py")}}, git_repo.env) == (0, "")


def test_other_tool_passes(pre, git_repo):
    assert pre.main({"tool_name": "Read", "tool_input": {}}, git_repo.env) == (0, "")


def test_internal_error_blocks_when_text_has_bypass_words(pre, git_repo, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(pre, "_decide", boom)
    code, err = bash(pre, git_repo, "git commit --no-verify")
    assert code == 2
    code, err = bash(pre, git_repo, "git -c core.hooksPath=x commit")
    assert code == 2
    assert bash(pre, git_repo, "python g.py --accept-b")[0] == 2
    code, err = bash(pre, git_repo, "git status")
    assert code == 0
    assert "warning" in err.lower()


def test_pretool_subprocess_blocks(git_repo):
    import os

    env = dict(os.environ, **git_repo.env)
    res = subprocess.run([sys.executable, str(HOOKS_DIR / "quality_gate_pretool.py")],
                         input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -n"}}),
                         text=True, capture_output=True, env=env, cwd=str(git_repo.root), timeout=60)
    assert res.returncode == 2
    assert "commit hooks must not be skipped" in res.stderr


def test_pretool_subprocess_bad_stdin_fails_open(git_repo):
    import os

    env = dict(os.environ, **git_repo.env)
    res = subprocess.run([sys.executable, str(HOOKS_DIR / "quality_gate_pretool.py")],
                         input="{no", text=True, capture_output=True, env=env,
                         cwd=str(git_repo.root), timeout=60)
    assert res.returncode == 0

"""Tests for the check_quality_gate plugin."""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

import pytest

import check_quality_gate as plugin

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def _stub(tmp_path, body):
    path = tmp_path / "stub.py"
    path.write_text(body, encoding="utf-8")
    return "%s %s" % (shlex.quote(sys.executable), shlex.quote(str(path)))


def _run(argv, cmd, quality_dir=None):
    def get(key, default=None):
        return cmd

    def get_path(key, default=None):
        return quality_dir

    return plugin.main(argv, get=get, get_path=get_path)


@pytest.mark.parametrize("value", [None, "", "  ", "{{GATE_FAST_CMD}}"])
def test_skip_when_not_installed(value, capsys):
    assert _run([], value) == 0
    assert "SKIP: quality gate not installed" in capsys.readouterr().out


def test_pass(tmp_path, capsys):
    cmd = _stub(
        tmp_path,
        'print(\'{"version":1,"status":"PASS","exit_code":0,"findings":[]}\')',
    )
    assert _run([], cmd) == 0
    assert "SKIP" not in capsys.readouterr().out


def test_fail_relays_findings_and_exit_code(tmp_path, capsys):
    payload = {
        "version": 1,
        "status": "FAIL",
        "exit_code": 4,
        "findings": [
            {"category": 4, "key": "pkg/mod.py::f", "message": "CRAP 31 > 30"}
        ],
    }
    cmd = _stub(tmp_path, "import json; print(json.dumps(%r))" % (payload,))
    assert _run([], cmd) == 4
    out = capsys.readouterr().out
    assert "[4] pkg/mod.py::f: CRAP 31 > 30" in out


def test_json_flag_passes_object_through(tmp_path, capsys):
    payload = {"version": 1, "status": "PASS", "exit_code": 0, "findings": []}
    cmd = _stub(tmp_path, "import json; print(json.dumps(%r))" % (payload,))
    assert _run(["--json"], cmd) == 0
    assert json.loads(capsys.readouterr().out) == payload


def test_non_json_exits_1(tmp_path, capsys):
    cmd = _stub(tmp_path, "print('hello world')")
    assert _run([], cmd) == 1


def test_wrong_version_exits_1(tmp_path):
    cmd = _stub(tmp_path, 'print(\'{"version":2,"exit_code":0}\')')
    assert _run([], cmd) == 1


def test_missing_command_exits_1(capsys):
    assert _run([], "definitely-not-a-real-binary-xyz") == 1


def test_env_gets_quality_dir(tmp_path, capsys):
    cmd = _stub(
        tmp_path,
        "import os, json\n"
        "print(json.dumps({'version':1,'status':'PASS','exit_code':0,"
        "'findings':[{'category':'env','key':'k','message':os.environ.get('SEJA_QUALITY_DIR','')}]}))",
    )
    assert _run([], cmd, quality_dir=tmp_path / "q") == 0
    assert str(tmp_path / "q") in capsys.readouterr().out


def _alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        with open("/proc/%d/stat" % pid) as fh:
            if fh.read().split(") ")[-1].startswith("Z"):
                return False
    except OSError:
        pass
    return True


def test_timeout_kills_group_and_exits_1(tmp_path, capsys):
    pidfile = tmp_path / "grandchild.pid"
    cmd = _stub(
        tmp_path,
        "import subprocess, sys, time\n"
        "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        "open(%r, 'w').write(str(p.pid))\n"
        "time.sleep(60)\n" % str(pidfile),
    )
    assert _run(["--timeout", "1"], cmd) == 1
    assert "timeout" in capsys.readouterr().out.lower()
    pid = int(pidfile.read_text())
    for _ in range(50):
        if not _alive(pid):
            break
        time.sleep(0.1)
    assert not _alive(pid)


def test_default_timeouts(tmp_path):
    assert plugin.DEFAULT_TIMEOUT == 110
    assert plugin.FULL_TIMEOUT == 1800


def test_full_uses_full_cmd():
    seen = []

    def get(key, default=None):
        seen.append(key)
        return None

    plugin.main(["--full"], get=get, get_path=lambda k, d=None: None)
    assert seen == ["GATE_FULL_CMD"]


def test_manifest_matches_registry():
    src = (SCRIPTS_DIR / "check_quality_gate.py").read_text(encoding="utf-8")
    block = src.split("CHECK_PLUGIN_MANIFEST:")[1]
    name = re.search(r"name:\s*(.+)", block).group(1).strip()
    backend = re.search(r"backend:\s*\[(.*?)\]", block).group(1).strip()
    frontend = re.search(r"frontend:\s*\[(.*?)\]", block).group(1).strip()
    scope = re.search(r"scope:\s*(\S+)", block).group(1)
    critical = re.search(r"critical:\s*(\S+)", block).group(1) == "true"
    registry = json.loads(
        (SCRIPTS_DIR / "check_plugin_registry.json").read_text(encoding="utf-8")
    )
    entry = [e for e in registry if e["script"] == "check_quality_gate.py"][0]
    assert entry["name"] == name == "Quality Gate"
    assert entry["stack"] == {"backend": [backend], "frontend": [frontend]}
    assert entry["scope"] == scope == "gate"
    assert entry["critical"] is critical is True

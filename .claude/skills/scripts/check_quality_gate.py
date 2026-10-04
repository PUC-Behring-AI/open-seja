#!/usr/bin/env python3
# designer: When your project has installed the quality gate, I run it for
#   you and relay each finding on its own line, with the gate's own exit
#   code. When the gate is not installed I say so and stay out of the way.
"""
check_quality_gate.py -- Run the project's quality gate, if installed.

Invocation: agent-invoked, hook-ci
Lifecycle: active

Reads GATE_FAST_CMD (or GATE_FULL_CMD with --full) from the project
conventions. A missing, empty or `{{...}}` placeholder value means the gate
is not installed: the plugin prints SKIP and exits 0. Otherwise it runs the
command (shlex, no shell) from the project root in its own process group,
parses the version 1 JSON report from stdout, prints one line per finding
as `[<category>] <key>: <message>`, and exits with the gate's exit_code.
Invalid JSON, a missing command or a timeout exit 1; on timeout the whole
process group is killed.

Usage
-----
    python3 .claude/skills/scripts/check_quality_gate.py [--full] [--json] [--timeout N]

CHECK_PLUGIN_MANIFEST:
  name: Quality Gate
  stack:
    backend: [any]
    frontend: [any]
  scope: gate
  critical: true
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import signal
import subprocess
import sys

import project_config

DEFAULT_TIMEOUT = 110  # below the fixed 120 s of run_all_checks.run_script
FULL_TIMEOUT = 1800
SKIP_MESSAGE = "SKIP: quality gate not installed"


def _not_installed(value):
    if value is None:
        return True
    text = str(value).strip()
    return not text or ("{{" in text and "}}" in text)


def _kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def _run_gate(argv_cmd, env, cwd, timeout):
    """Return (returncode, stdout, timed_out)."""
    proc = subprocess.Popen(
        argv_cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        return None, "", True
    if err:
        sys.stderr.write(err)
    return proc.returncode, out, False


def main(argv=None, get=project_config.get, get_path=project_config.get_path):
    parser = argparse.ArgumentParser(description="Run the project quality gate")
    parser.add_argument("--full", action="store_true", help="use GATE_FULL_CMD")
    parser.add_argument("--json", action="store_true", help="print the gate JSON")
    parser.add_argument("--timeout", type=int, default=None)
    args = parser.parse_args(argv)

    key = "GATE_FULL_CMD" if args.full else "GATE_FAST_CMD"
    value = get(key)
    if _not_installed(value):
        print(SKIP_MESSAGE)
        return 0

    timeout = args.timeout
    if timeout is None:
        timeout = FULL_TIMEOUT if args.full else DEFAULT_TIMEOUT

    env = dict(os.environ)
    quality_dir = get_path("QUALITY_DIR")
    if quality_dir:
        env["SEJA_QUALITY_DIR"] = str(quality_dir)

    try:
        cmd = shlex.split(str(value))
        returncode, out, timed_out = _run_gate(cmd, env, str(project_config.REPO_ROOT), timeout)
    except (OSError, ValueError) as exc:
        print("ERROR: cannot run %s: %s" % (key, exc))
        return 1

    if timed_out:
        print("ERROR: quality gate timeout after %d s (process group killed)" % timeout)
        return 1

    try:
        report = json.loads(out)
        if not isinstance(report, dict) or report.get("version") != 1:
            raise ValueError("unsupported report version")
        code = int(report.get("exit_code", 1))
    except (ValueError, TypeError) as exc:
        print("ERROR: quality gate did not return a valid version 1 JSON report: %s" % exc)
        return 1

    if args.json:
        print(json.dumps(report))
        return code

    for finding in report.get("findings", []):
        print("[%s] %s: %s" % (finding.get("category"), finding.get("key"), finding.get("message")))
    print("quality gate: %s (exit %d)" % (report.get("status", "?"), code))
    return code


if __name__ == "__main__":
    sys.exit(main())

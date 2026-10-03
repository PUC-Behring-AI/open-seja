#!/usr/bin/env python3
"""Claude Code Stop hook: hold the end of a turn while the quality gate is red.

Reads the hook payload (JSON) on stdin. Exit 0 releases the turn; exit 2 blocks
it and returns stderr to the agent. Inert unless GATE_FAST_CMD is set in
product-design/conventions.md. Stdlib only; shared code is in _gate_hook_common.py.

After 3 consecutive blocks in a session (stop_hook_active=true) the turn is
released so the human decides. Internal errors fail open with a warning.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _gate_hook_common as common  # noqa: E402

MAX_BLOCKS = 3


def _decide(payload, env):
    cwd = common.project_dir(payload, env)
    conv = common.parse_conventions(cwd)
    cmd = conv.get("GATE_FAST_CMD")
    if common.is_unset(cmd):
        return 0, ""
    files = common.changed_py_files(cwd)
    if not files:
        return 0, ""
    session = payload.get("session_id")
    state = common.load_state(env, session)
    blocks = int(state.get("blocks", 0)) if payload.get("stop_hook_active") else 0
    if blocks >= MAX_BLOCKS:
        common.save_state(env, session, {"blocks": 0})
        last = state.get("last_findings") or ""
        return 0, ("Quality gate: released after %d blocks; the human decides.\n" % MAX_BLOCKS) + last
    digest = common.state_hash(cwd, files, cmd)
    if state.get("pass_hash") == digest:
        common.save_state(env, session, {"blocks": 0, "pass_hash": digest})
        return 0, ""
    result = common.run_gate(cmd, files, cwd, common.hook_timeout(env))
    if result.passed:
        common.save_state(env, session, {"blocks": 0, "pass_hash": digest})
        return 0, ""
    message = common.block_message(result)
    common.save_state(env, session, {"blocks": blocks + 1, "last_findings": message})
    return 2, message


def main(payload, env):
    """Return (exit_code, stderr_text). Fails open on internal errors."""
    try:
        return _decide(payload, env)
    except Exception as err:  # noqa: BLE001 - a broken hook must not trap the agent
        return 0, "warning: quality_gate_stop hook failed open: %s: %s\n" % (type(err).__name__, err)


def _cli():
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("payload is not a JSON object")
    except ValueError as err:
        sys.stderr.write("warning: quality_gate_stop hook failed open: bad payload: %s\n" % err)
        return 0
    code, err_text = main(payload, dict(os.environ))
    if err_text:
        sys.stderr.write(err_text)
    return code


if __name__ == "__main__":
    sys.exit(_cli())

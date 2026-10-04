"""Shared helpers for the quality-gate hooks (stdlib only).

Used by quality_gate_stop.py and quality_gate_pretool.py. Hooks run with only
their own directory on sys.path[0], so this file must not import the harness
(.claude/skills/scripts may be absent). The conventions parser mirrors
project_config.py (same row regex, same shell-metacharacter rejection, same
${VAR} resolution); tests/test_quality_gate_hooks.py checks the parity.
"""
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import tempfile

ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|", re.MULTILINE)
VAR_REF_RE = re.compile(r"\$\{([^}]+)\}")
SHELL_INJECTION_RE = re.compile(r"`|\$\(|\$\(\(")
MAX_RESOLVE_PASSES = 10
DEFAULT_TIMEOUT = 120
PLACEHOLDER_RE = re.compile(r"^\{\{.*\}\}$")


def parse_rows(text):
    """Return the raw {variable: value} rows of a conventions table."""
    return {m.group(1): m.group(2) for m in ROW_RE.finditer(text)}


def parse_conventions(project_dir):
    """Read product-design/conventions.md; resolve ${VAR}; drop tainted rows."""
    path = os.path.join(str(project_dir), "product-design", "conventions.md")
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw = parse_rows(fh.read())
    except OSError:
        return {}
    resolved = {k: v for k, v in raw.items() if not SHELL_INJECTION_RE.search(v)}
    for _ in range(MAX_RESOLVE_PASSES):
        changed = False
        for key, value in resolved.items():
            new = VAR_REF_RE.sub(lambda m: resolved.get(m.group(1), m.group(0)), value)
            if new != value:
                resolved[key] = new
                changed = True
        if not changed:
            break
    return resolved


def is_unset(value):
    """True when a GATE_* value means "gate not installed"."""
    return value is None or not value.strip() or bool(PLACEHOLDER_RE.match(value.strip()))


def project_dir(payload, env):
    return env.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()


def hook_timeout(env, default=DEFAULT_TIMEOUT):
    try:
        value = float(env.get("SEJA_GATE_HOOK_TIMEOUT", ""))
    except ValueError:
        return default
    return value if value > 0 else default


def _git(cwd, *args):
    res = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return res.stdout if res.returncode == 0 else ""


def changed_py_files(cwd):
    """Modified (vs HEAD, deletions excluded) plus untracked .py files, sorted."""
    names = set(_git(cwd, "diff", "--name-only", "--diff-filter=d", "HEAD").splitlines())
    names.update(_git(cwd, "ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(n for n in names if n.endswith(".py") and os.path.isfile(os.path.join(cwd, n)))


def staged_py_files(cwd):
    names = _git(cwd, "diff", "--cached", "--name-only", "--diff-filter=d").splitlines()
    return sorted(n for n in names if n.endswith(".py"))


def state_hash(cwd, files, cmd):
    """Hash of (git diff HEAD, untracked contents, gate command)."""
    digest = hashlib.sha256()
    digest.update(_git(cwd, "diff", "HEAD").encode())
    untracked = set(_git(cwd, "ls-files", "--others", "--exclude-standard").splitlines())
    for name in files:
        if name in untracked:
            digest.update(name.encode())
            with open(os.path.join(cwd, name), "rb") as fh:
                digest.update(fh.read())
    digest.update(cmd.encode())
    return digest.hexdigest()


class GateResult:
    def __init__(self, status, exit_code, findings):
        self.status = status
        self.exit_code = exit_code
        self.findings = findings

    @property
    def passed(self):
        return self.status == "PASS"


def _kill_group(proc):
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, AttributeError):
        proc.kill()


def format_finding(item):
    return "[%s] %s: %s" % (item.get("category"), item.get("key"), item.get("message"))


def _parse_report(out, returncode):
    try:
        report = json.loads(out)
        if not isinstance(report, dict) or report.get("version") != 1:
            raise ValueError("unsupported report version")
        code = int(report.get("exit_code", returncode))
        status = str(report.get("status", "ERROR"))
        findings = [format_finding(f) for f in report.get("findings", []) if isinstance(f, dict)]
    except (ValueError, TypeError):
        return GateResult("ERROR", 1, ["[1] gate: the gate did not return a valid version 1 JSON report (exit %s)" % returncode])
    if status == "PASS" and (code != 0 or returncode != 0):
        return GateResult("ERROR", 1, ["[1] gate: report says PASS but the exit code is %s" % (code or returncode)])
    return GateResult(status, code, findings)


def run_gate(cmd, files, cwd, timeout):
    """Run `<cmd> --files <files>`; return a GateResult. Never raises on gate failure."""
    try:
        argv = shlex.split(cmd) + ["--files", *files]
        proc = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, start_new_session=True)
    except (OSError, ValueError) as err:
        return GateResult("ERROR", 1, ["[1] gate: cannot run the gate command: %s" % err])
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_group(proc)
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        return GateResult("ERROR", 1, ["[1] gate: timeout after %g s (process group killed)" % timeout])
    return _parse_report(out, proc.returncode)


def block_message(result):
    lines = ["Quality gate %s (exit %d):" % (result.status, result.exit_code)]
    lines.extend(result.findings)
    return "\n".join(lines) + "\n"


def _state_path(env, session_id):
    root = env.get("TMPDIR") or env.get("TEMP") or env.get("TMP") or tempfile.gettempdir()
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_id or "unknown")).lstrip(".") or "unknown"
    return os.path.join(root, "seja-gate", safe + ".json")


def load_state(env, session_id):
    try:
        with open(_state_path(env, session_id), encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(env, session_id, state):
    """Atomic write (temp file in the same directory + os.replace)."""
    path = _state_path(env, session_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

#!/usr/bin/env python3
"""Claude Code PreToolUse hook: guard the quality baseline and `git commit`.

Reads the hook payload (JSON) on stdin. Exit 0 allows the tool call; exit 2 blocks
it and returns stderr to the agent. Matcher: Bash|Edit|Write|MultiEdit.

- Edit/Write/MultiEdit on quality-baseline.json: blocked (only a human moves it).
- Bash, always (gate installed or not): --accept-baseline (any prefix of >= --acc)
  on gate.py or a GATE_* command; skipping commit hooks (--no-verify and its
  abbreviations, -n, -c core.hooksPath, --config-env); commits that change GATE_*
  lines of product-design/conventions.md.
- Bash `git commit` with GATE_COMMIT_CMD set: runs it on the staged, modified and
  untracked .py files (600 s, SEJA_GATE_HOOK_TIMEOUT overrides, no cache); blocks
  on FAIL, ERROR or timeout.

This is a guard against an agent's slips, not a sandbox: see the limits in the
README of the quality gate. Stdlib only; shared code is in _gate_hook_common.py.
"""
import json
import os
import re
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _gate_hook_common as common  # noqa: E402

COMMIT_TIMEOUT = 600
BASELINE_NAME = "quality-baseline.json"
MSG_BASELINE = "Blocked: only a human moves the quality baseline. Do not edit %s or pass --accept-baseline; report the finding instead.\n" % BASELINE_NAME
MSG_HOOKS = "Blocked: commit hooks must not be skipped (--no-verify, -n, core.hooksPath, --config-env). Fix the findings and commit normally.\n"
MSG_CONFIG = "Blocked: gate config must be committed by a human. This commit changes GATE_ lines of product-design/conventions.md.\n"
RAW_WORDS = ("no-verify", "hookspath", "accept-b")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
PREFIX_CMDS = {"env", "command", "exec", "nohup", "time", "sudo", "nice"}
SEPARATORS = {"&&", "||", ";", "|", "&", ";;", "|&", "(", ")"}
LONG_ARG_OPTS = {"--message", "--file", "--author", "--date", "--template", "--reuse-message",
                 "--reedit-message", "--fixup", "--squash", "--cleanup", "--trailer", "--pathspec-from-file"}
ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


class Blocked(Exception):
    pass


def _split_lines(text):
    """Turn unquoted newlines into ';' so shlex sees them as separators."""
    out, quote, escaped = [], None, False
    for ch in text:
        if escaped:
            escaped = False
        elif ch == "\\" and quote != "'":
            escaped = True
        elif quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "\n":
            ch = " ; "
        out.append(ch)
    return "".join(out)


def split_segments(text):
    """Tokenize a shell command line into segments (lists of words). Tolerant to errors."""
    text = _split_lines(text)
    lex = shlex.shlex(text, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    segments, cur = [], []
    try:
        for tok in lex:
            if tok in SEPARATORS:
                segments.append(cur)
                cur = []
            else:
                cur.append(tok)
    except ValueError:
        # unbalanced quote: fall back to what we have plus a plain split of the rest
        cur.extend(text.split())
    segments.append(cur)
    return [s for s in segments if s]


def _gate_keys(conv):
    keys = {"gate.py"}
    for name in ("GATE_FAST_CMD", "GATE_FULL_CMD", "GATE_COMMIT_CMD"):
        value = conv.get(name)
        if common.is_unset(value):
            continue
        try:
            words = [w for w in shlex.split(value) if not w.startswith("-")]
        except ValueError:
            continue
        if words:
            keys.add(os.path.basename(words[-1]))
    return keys


def _git_alias(cwd, sub):
    res = subprocess.run(["git", "config", "--get", "alias." + sub], cwd=cwd,
                         capture_output=True, text=True)
    return res.stdout.strip() if res.returncode == 0 else ""


def _skip_global(words):
    """Return (sub, rest, config_pairs, flags) after git's global options."""
    configs, flags, i = [], [], 1
    while i < len(words):
        w = words[i]
        if w == "-c" and i + 1 < len(words):
            configs.append(words[i + 1])
            i += 2
        elif w.startswith("-c") and len(w) > 2 and not w.startswith("--"):
            configs.append(w[2:])
            i += 1
        elif w in ("-C", "--git-dir", "--work-tree", "--namespace", "--exec-path") and i + 1 < len(words):
            i += 2
        elif w == "--config-env":
            flags.append("config-env")
            i += 2
        elif w.startswith("--config-env="):
            flags.append("config-env")
            i += 1
        elif w.startswith("-"):
            i += 1
        else:
            return w, words[i + 1:], configs, flags
    return None, [], configs, flags


def _commit_skips_hooks(args):
    """True if `git commit <args>` skips hooks via -n / --no-verify (or abbreviation)."""
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--":
            return False
        if a.startswith("--"):
            name = a.split("=", 1)[0]
            if len(name) >= 6 and "--no-verify".startswith(name):
                return True
            if name in LONG_ARG_OPTS and "=" not in a:
                i += 1
        elif a.startswith("-") and len(a) > 1:
            for pos, ch in enumerate(a[1:], 1):
                if ch == "n":
                    return True
                if ch in "mFCct":
                    if pos == len(a) - 1:
                        i += 1
                    break
                if ch in "Su":
                    break
        i += 1
    return False


def _writes_baseline(words):
    names = [os.path.basename(w) == BASELINE_NAME for w in words]
    if not any(names):
        return False
    first = os.path.basename(words[0])
    if first in ("tee", "rm", "mv", "cp", "truncate", "dd", "ed"):
        return True
    if first == "sed" and any(w.startswith("-i") or w == "--in-place" for w in words):
        return True
    return any(n and idx > 0 and words[idx - 1].startswith(">") for idx, n in enumerate(names))


class Analysis:
    def __init__(self, cwd, keys):
        self.cwd = cwd
        self.keys = keys
        self.commit = False

    def segment(self, words, depth=0):
        if depth > 5 or not words:
            return
        i = 0
        while i < len(words):
            w = words[i]
            if ASSIGN_RE.match(w) or os.path.basename(w) in PREFIX_CMDS or (w.startswith("-") and i > 0 and ASSIGN_RE.match(words[i - 1]) is None and os.path.basename(words[0]) in PREFIX_CMDS):
                i += 1
            else:
                break
        words = words[i:]
        if not words:
            return
        base = os.path.basename(words[0])
        if _writes_baseline(words):
            raise Blocked(MSG_BASELINE)
        if any(os.path.basename(w) in self.keys for w in words) and any(
                w.startswith("--acc") and len(w.split("=", 1)[0]) >= 5
                and "--accept-baseline".startswith(w.split("=", 1)[0]) for w in words):
            raise Blocked(MSG_BASELINE)
        if base in SHELLS or base == "eval":
            self._nested(words, base, depth)
        elif base == "git":
            self._git(words, depth)

    def _nested(self, words, base, depth):
        if base == "eval":
            self.text(" ".join(words[1:]), depth + 1)
            return
        for idx, w in enumerate(words[1:], 1):
            if w.startswith("-") and not w.startswith("--") and "c" in w and idx + 1 < len(words):
                self.text(words[idx + 1], depth + 1)
                return

    def text(self, text, depth=0):
        for seg in split_segments(text):
            self.segment(seg, depth)

    def _git(self, words, depth):
        sub, rest, configs, flags = _skip_global(words)
        if sub is None:
            return
        for _ in range(5):
            alias = _git_alias(self.cwd, sub)
            if not alias:
                break
            if alias.startswith("!"):
                self.text(alias[1:] + " " + " ".join(shlex.quote(r) for r in rest), depth + 1)
                return
            try:
                expanded = shlex.split(alias)
            except ValueError:
                break
            if not expanded:
                break
            sub, rest = expanded[0], expanded[1:] + rest
        if sub != "commit":
            return
        self.commit = True
        if "config-env" in flags or any(r.startswith("--config-env") for r in rest) or any(c.lower().startswith("core.hookspath") for c in configs):
            raise Blocked(MSG_HOOKS)
        if _commit_skips_hooks(rest):
            raise Blocked(MSG_HOOKS)


def _gate_lines_changed(cwd):
    res = subprocess.run(["git", "diff", "HEAD", "--", "product-design/conventions.md"],
                         cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        return False
    return any(line[:1] in "+-" and not line.startswith(("+++", "---")) and "GATE_" in line
               for line in res.stdout.splitlines())


def _decide(payload, env):
    tool = payload.get("tool_name")
    tin = payload.get("tool_input") or {}
    if tool in ("Edit", "Write", "MultiEdit"):
        path = str(tin.get("file_path", ""))
        if os.path.basename(path.replace("\\", "/")) == BASELINE_NAME:
            return 2, MSG_BASELINE
        return 0, ""
    if tool != "Bash":
        return 0, ""
    command = str(tin.get("command", ""))
    cwd = common.project_dir(payload, env)
    conv = common.parse_conventions(cwd)
    analysis = Analysis(cwd, _gate_keys(conv))
    try:
        analysis.text(command)
    except Blocked as blocked:
        return 2, str(blocked)
    if not analysis.commit:
        return 0, ""
    if _gate_lines_changed(cwd):
        return 2, MSG_CONFIG
    cmd = conv.get("GATE_COMMIT_CMD")
    if common.is_unset(cmd):
        return 0, ""
    files = sorted(set(common.changed_py_files(cwd)) | set(common.staged_py_files(cwd)))
    if not files:
        return 0, ""
    result = common.run_gate(cmd, files, cwd, common.hook_timeout(env, COMMIT_TIMEOUT))
    if result.passed:
        return 0, ""
    return 2, common.block_message(result)


def _raw_text(payload):
    tin = payload.get("tool_input") if isinstance(payload, dict) else None
    return json.dumps(tin if tin is not None else payload, default=str)


def main(payload, env):
    """Return (exit_code, stderr_text). Fails open on internal errors, except on bypass words."""
    try:
        return _decide(payload, env)
    except Exception as err:  # noqa: BLE001 - a broken hook must not trap the agent
        raw = _raw_text(payload).lower()
        if any(word in raw for word in RAW_WORDS) or BASELINE_NAME in raw:
            return 2, "Blocked: quality_gate_pretool failed (%s: %s) on a command that looks like a gate bypass.\n" % (type(err).__name__, err)
        return 0, "warning: quality_gate_pretool hook failed open: %s: %s\n" % (type(err).__name__, err)


def _cli():
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("payload is not a JSON object")
    except ValueError as err:
        sys.stderr.write("warning: quality_gate_pretool hook failed open: bad payload: %s\n" % err)
        return 0
    code, err_text = main(payload, dict(os.environ))
    if err_text:
        sys.stderr.write(err_text)
    return code


if __name__ == "__main__":
    sys.exit(_cli())

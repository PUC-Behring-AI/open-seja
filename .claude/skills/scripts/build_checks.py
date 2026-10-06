#!/usr/bin/env python3
# designer: When I build a step from your approved scenarios, I use these checks so that
#   every move is a tool's answer and not my sentence: the test failed for the right
#   reason, nobody touched the frozen tests, each role stayed in its lane, the quality
#   baseline did not move, and what was built is recorded where the drift report reads it.
"""
build_checks -- deterministic checks of the test-first branch of /implement (ITF-001..025).

Invocation: skill-invoked (/implement), agent-invoked
Lifecycle: active

Rules: .claude/references/general/implement-test-first.md. Standard library only; no LLM, no
network, no clock outside --at.

Exit codes: 0 ok, 1 finding, 2 usage error, unreadable or missing input.

Usage:
    python3 .claude/skills/scripts/build_checks.py install-plugin <project>

(Step 4 of plan-000013 delivers install-plugin; the other subcommands come in Step 5.)
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

PLUGIN_SOURCE = (Path(__file__).resolve().parents[2] / "references" / "template" / "bdd" / "python"
                 / "scenario_report.py.example")
PLUGIN_LINE = 'pytest_plugins = ["scenario_report"]'
PLUGIN_STAMP = ".scenario_report.sha256"


class BuildError(Exception):
    """Exit 2: usage error, unreadable or missing input."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def install_plugin(project: Path, source: Path = PLUGIN_SOURCE) -> tuple[int, str]:
    """Copy the plugin to <project>/tests/scenario_report.py and load it from tests/conftest.py.

    Idempotent. Refuses (1) to overwrite a copy edited by hand since the last install.
    """
    try:
        new = source.read_bytes()
    except OSError as err:
        raise BuildError(f"plugin template not readable: {source}") from err
    tests = project / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    target = tests / "scenario_report.py"
    stamp = tests / PLUGIN_STAMP
    if target.exists():
        current = target.read_bytes()
        recorded = stamp.read_text(encoding="utf-8").strip() if stamp.exists() else None
        if _sha(current) != _sha(new) and _sha(current) != recorded:
            return 1, f"{target}: copia editada a mao; nao sobrescrevi. Apague-a para reinstalar."
    target.write_bytes(new)
    stamp.write_text(_sha(new) + "\n", encoding="utf-8")
    conftest = tests / "conftest.py"
    text = conftest.read_text(encoding="utf-8-sig") if conftest.exists() else ""
    if PLUGIN_LINE not in text:
        prefix = text if not text or text.endswith("\n") else text + "\n"
        conftest.write_text(prefix + PLUGIN_LINE + "\n", encoding="utf-8")
    return 0, f"{target} ({_sha(new)[:12]})"


# --- pending (Step 5) ---------------------------------------------------------------------------


def red_check(report, owned, **kw):
    return {"ok": None, "findings": [], "scenarios": {}, "escalate": None}


def report_from_cucumber(cucumber, junit=None, expected=None):
    return {"scenarios": {}}


def check_skeleton(paths):
    return None


def green_check(report, owned):
    return {"ok": None, "findings": [], "final": {}}


def freeze_snapshot(root, files):
    return {}


def freeze_compare(root, snapshot):
    return None


def check_scope(role, changes, frozen, added):
    return None


def parse_diff_added(diff):
    return {}


def uncovered(added, coverage):
    return {}


def baseline_state(before, after, known=True):
    return {}


def crap_findings(radon, coverage, files, target=8):
    return None


def record(gate, step, payload, at, plan=None):
    return {}


def next_phase(gate, step, pipeline=False):
    return None


def route(text, pipeline=False):
    return {}


def export_files(gate, slug, cucumber=None):
    return {}


def demo_text(gate, steps, questions):
    return ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="build_checks.py", description=__doc__.splitlines()[1])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("install-plugin", help="copy the runner report plugin into <project>/tests (ITF-016)")
    p.add_argument("project", type=Path)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    try:
        code, message = install_plugin(args.project)
    except (BuildError, OSError) as err:
        print(f"build_checks: {err}", file=sys.stderr)
        return 2
    print(message, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())

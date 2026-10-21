#!/usr/bin/env python3
# designer: When I change what the upgrade removes or warns about, I run it
#   on small copies of real client projects (one installed with v0.11.0,
#   one with v0.10.1) and tell you which files it removed, which it kept
#   because you edited them, which it copied, and what it warned -- so a
#   client upgrade is rehearsed before it happens.
"""
run_upgrade_compat.py -- Run upgrade_harness.py on a copy of a client fixture.

Invocation: test-helper (tests/compat/test_upgrade_compat.py) and manual
Lifecycle: active

The fixture is copied to a temporary directory (the fixture itself is never
changed), the upgrade runs from this repository's harness, and the report is
parsed from its output.

Exit codes: 0 = upgrade ran, 1 = upgrade failed, 2 = usage error.

Usage
-----
    python tests/compat/run_upgrade_compat.py tests/compat/fixtures/client-v0.11.0
    python tests/compat/run_upgrade_compat.py <fixture> --keep <dir>
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UPGRADE = REPO_ROOT / ".claude" / "skills" / "scripts" / "upgrade_harness.py"
SCHEMA_VERSION = 1

_REMOVED_RE = re.compile(r"^OK: removido (\S+)$")
_HOOK_RE = re.compile(r"^OK: plugin desligado em (\S+)$")
_KEPT_RE = re.compile(r"^WARN: mantido \(editado\) (\S+)$")
_COPIED_RE = re.compile(r"^OK: Updated (\S+)$")
_WARN_RE = re.compile(r"^WARN: (?!mantido \(editado\))(.+)$")


def parse_output(stdout: str) -> dict:
    report: dict = {"removed": [], "removed_hooks": [], "kept": [], "copied": [], "warnings": []}
    for raw in stdout.splitlines():
        line = raw.strip()
        if m := _REMOVED_RE.match(line):
            report["removed"].append(m.group(1))
        elif m := _HOOK_RE.match(line):
            report["removed_hooks"].append(m.group(1))
        elif m := _KEPT_RE.match(line):
            report["kept"].append(m.group(1))
        elif m := _COPIED_RE.match(line):
            report["copied"].append(m.group(1))
        elif m := _WARN_RE.match(line):
            report["warnings"].append(m.group(1))
    return report


def run(fixture: Path, workdir: Path, client_local: bool = False) -> dict:
    """Copy `fixture` into `workdir/target`, upgrade it, and return the parsed report.

    With `client_local`, this repository's upgrade_harness.py is first copied into
    the target (without retired-files.json beside it) and run from there, so the
    retired list must come from the source tree passed in --from.
    """
    target = workdir / "target"
    shutil.copytree(fixture, target)
    script = UPGRADE
    if client_local:
        script = target / UPGRADE.relative_to(REPO_ROOT)
        script.parent.mkdir(parents=True, exist_ok=True)
        for py in UPGRADE.parent.glob("*.py"):  # the .py scripts a client has, no .json
            shutil.copy2(py, script.parent / py.name)
    proc = subprocess.run(
        [sys.executable, str(script), "--from", str(REPO_ROOT), "--target", str(target)],
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    report = parse_output(proc.stdout)
    report.update(
        {"schema_version": SCHEMA_VERSION, "returncode": proc.returncode, "target": str(target)}
    )
    if proc.returncode != 0:
        report["stderr"] = proc.stderr
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the upgrade on a copy of a client fixture")
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--keep", type=Path, help="work in this (empty) directory and keep it")
    args = parser.parse_args(argv)
    if not (args.fixture / ".claude").is_dir():
        parser.error(f"fixture has no .claude/: {args.fixture}")
    if args.keep:
        args.keep.mkdir(parents=True, exist_ok=True)
        report = run(args.fixture, args.keep)
    else:
        with tempfile.TemporaryDirectory(prefix="seja-compat-") as tmp:
            report = run(args.fixture, Path(tmp))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["returncode"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

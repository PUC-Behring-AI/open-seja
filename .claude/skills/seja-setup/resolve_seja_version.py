#!/usr/bin/env python3
# designer: When /seja-setup needs to pin your project against a concrete
#   open-seja release, I'm the resolver that asks the open-seja remote for its
#   current tag list and hands back the version to use -- the newest SemVer
#   tag by default, or whichever tag you named with --version. You get a
#   deterministic answer instead of an implicit "whatever is on main today".
"""resolve_seja_version.py -- Resolve the open-seja release tag to pin against.

Invocation: skill-invoked, user-cli
Lifecycle: active

Used by `/seja-setup` (install and --upgrade modes) to turn a `--version <tag>` request into a concrete
SemVer tag name (e.g. `v0.1.0`) discovered on the open-seja remote
(`git@github.com:PUC-Behring-AI/open-seja.git`; override with the `SEJA_REMOTE` environment variable or `--remote`).
Defaults to the newest SemVer tag. Falls back to `HEAD` (with a warning) when the
remote has no SemVer tags yet.

CLI:
    python resolve_seja_version.py [--remote <url>] [--version <tag>]

Library:
    from resolve_seja_version import resolve_version, fetch_remote_tags
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
DEFAULT_REMOTE = "git@github.com:PUC-Behring-AI/open-seja.git"
REMOTE_ENV_VAR = "SEJA_REMOTE"
HEAD_SENTINEL = "HEAD"


def parse_ls_remote_tags(output: str) -> list[str]:
    """Parse `git ls-remote --tags <url>` output; return SemVer tags oldest -> newest.

    Skips peeled refs (`^{}` suffix) and non-SemVer tag names.
    """
    parsed: list[tuple[tuple[int, int, int], str]] = []
    for line in output.splitlines():
        parts = line.split("refs/tags/")
        if len(parts) != 2:
            continue
        name = parts[1].strip()
        if name.endswith("^{}"):
            continue
        m = TAG_RE.match(name)
        if not m:
            continue
        key = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        parsed.append((key, name))
    parsed.sort(key=lambda t: t[0])
    return [name for _, name in parsed]


def fetch_remote_tags(remote: str) -> list[str]:
    """Run `git ls-remote --tags <remote>` and return SemVer tags oldest -> newest."""
    result = subprocess.run(
        ["git", "ls-remote", "--tags", remote],
        capture_output=True,
        text=True,
        timeout=30,
        # Never block on a credential prompt; fail fast and print the hint instead.
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    if result.returncode != 0:
        raise RuntimeError(f"git ls-remote failed: {result.stderr.strip()}")
    return parse_ls_remote_tags(result.stdout)


def resolve_version(
    requested: str | None,
    available: list[str],
) -> tuple[str, str | None]:
    """Resolve a requested version against the available tag list.

    Returns (resolved_ref, warning). `resolved_ref` is the SemVer tag to check out,
    or `HEAD` if no SemVer tags exist. `warning` is None on the happy path.
    """
    if not available:
        return (
            HEAD_SENTINEL,
            "No SemVer tags found on remote -- falling back to HEAD.",
        )
    if requested in (None, "latest"):
        return (available[-1], None)
    if requested in available:
        return (requested, None)
    return (
        requested,
        f"Requested version {requested} not found in remote tags "
        f"(available: {', '.join(available)}).",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve a seja release tag.")
    parser.add_argument(
        "--remote",
        default=os.environ.get(REMOTE_ENV_VAR, DEFAULT_REMOTE),
        help=(
            f"Remote URL to query tags from (default: ${REMOTE_ENV_VAR}, "
            f"else {DEFAULT_REMOTE})"
        ),
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Requested version (e.g. v0.1.0 or 'latest'). Default: latest.",
    )
    args = parser.parse_args(argv)

    try:
        available = fetch_remote_tags(args.remote)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            f"hint: set {REMOTE_ENV_VAR}=https://github.com/PUC-Behring-AI/open-seja "
            "or pass --remote",
            file=sys.stderr,
        )
        return 2

    resolved, warning = resolve_version(args.version, available)
    if warning:
        print(f"WARN: {warning}", file=sys.stderr)
    print(resolved)
    return 0


if __name__ == "__main__":
    sys.exit(main())

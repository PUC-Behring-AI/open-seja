#!/usr/bin/env python3
"""build_dist_branch.py -- Write open-seja's distribution branch as a snapshot of the dev branch.

Development happens on `dev`, which tracks the project's own `product-design/`, `_output/` and `tools/`.
The distribution branch (`main`) carries only the public surface defined by `tools/publish-manifest.txt`,
minus `product-design/` (a clone that carries it is detected as `partial-init` by /seja-setup --here).

Each release is one commit on `main` whose tree is the pruned tree of `dev` and whose only parent is the
previous `main`. Nothing is merged: `dev`'s history is not reachable from `main`. The script reads
everything from refs through a temporary index; it never touches the working tree or the real index.

Usage (run from a checkout of dev; see tools/release-process.md):
    python tools/build_dist_branch.py --dry-run     # list what would be pruned
    python tools/build_dist_branch.py               # write the release commit on main
    python tools/build_dist_branch.py --check       # verify main holds only the public surface

Exit codes: 0 ok; 1 surface violated or nothing to release; 2 git error.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

MANIFEST_PATH = "tools/publish-manifest.txt"
EXTRA_PATHSPECS = (":(exclude,glob)product-design/**",)


class GitError(Exception):
    """A git command failed."""


def git(*args: str, env: dict[str, str] | None = None, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, env=env, input=input_text
    )
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def read_pathspecs(source: str) -> list[str]:
    manifest = git("show", f"{source}:{MANIFEST_PATH}")
    specs = [
        line.strip()
        for line in manifest.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    return specs + list(EXTRA_PATHSPECS)


def ls_files(env: dict[str, str], pathspecs: list[str] | None = None) -> set[str]:
    args = ["ls-files", "-z"]
    if pathspecs:
        args += ["--", *pathspecs]
    # Deduplicated: a path can appear once per stage.
    return {p for p in git(*args, env=env).split("\0") if p}


def pruned_tree(source: str, pathspecs: list[str], index_file: str) -> tuple[str, list[str]]:
    env = {**os.environ, "GIT_INDEX_FILE": index_file}
    git("read-tree", source, env=env)
    removed = sorted(ls_files(env) - ls_files(env, pathspecs))
    if removed:
        # Literal pathspecs: the removed entries are file names, not patterns.
        git("rm", "-q", "--cached", "--pathspec-from-file=-", "--pathspec-file-nul",
            env={**env, "GIT_LITERAL_PATHSPECS": "1"}, input_text="\0".join(removed))
    return git("write-tree", env=env).strip(), removed


def release_label(source: str) -> str:
    changelog = git("show", f"{source}:CHANGELOG.md")
    match = re.search(r"^## \[v?(\d+\.\d+\.\d+)\]", changelog, flags=re.M)
    return f"v{match.group(1)}" if match else "unversioned"


def check_target(source: str, target: str, pathspecs: list[str]) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": os.path.join(tmp, "index")}
        git("read-tree", target, env=env)
        return sorted(ls_files(env) - ls_files(env, pathspecs))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", default="dev", help="ref to snapshot (default: dev)")
    parser.add_argument("--target", default="main", help="distribution branch (default: main)")
    parser.add_argument("--message", default=None, help="release commit message")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="list pruned paths; write nothing")
    mode.add_argument("--check", action="store_true", help="fail if target holds paths outside the surface")
    args = parser.parse_args(argv)

    try:
        pathspecs = read_pathspecs(args.source)
        if args.check:
            outside = check_target(args.source, args.target, pathspecs)
            for path in outside:
                print(f"outside surface: {path}", file=sys.stderr)
            if outside:
                return 1
            print(f"{args.target}: only the public surface ({MANIFEST_PATH} of {args.source})")
            return 0

        source_sha = git("rev-parse", "--verify", f"{args.source}^{{commit}}").strip()
        target_sha = git("rev-parse", "--verify", f"refs/heads/{args.target}").strip()
        with tempfile.TemporaryDirectory() as tmp:
            tree, removed = pruned_tree(source_sha, pathspecs, os.path.join(tmp, "index"))

        if args.dry_run:
            for path in removed:
                print(f"prune: {path}")
            print(f"{len(removed)} paths pruned; tree {tree}")
            return 0

        if tree == git("rev-parse", f"{target_sha}^{{tree}}").strip():
            print(f"{args.target} already has this tree; nothing to release", file=sys.stderr)
            return 1
        message = args.message or (
            f"Release {release_label(source_sha)} "
            f"(distribution tree of {args.source} {source_sha[:7]})"
        )
        commit = git("commit-tree", tree, "-p", target_sha, "-m", message).strip()
        git("update-ref", f"refs/heads/{args.target}", commit, target_sha)
        print(f"{args.target} -> {commit[:7]} ({len(removed)} paths pruned): {message}")
        return 0
    except GitError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

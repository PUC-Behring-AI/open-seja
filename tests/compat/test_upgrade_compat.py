"""Upgrade-by-tag compatibility proof as a pytest (plan-000015, Step 9).

Invocation: test
Lifecycle: active

Runs `run_upgrade_compat.py` against this repository's working tree: the four projects are generated from the
previous tag, upgraded offline to the not-yet-tagged working tree (the tag exists only inside a throw-away clone)
and compared. One full run takes about 20 s; the result is shared by the tests of the module. Skipped when the
previous tag is not in the repository (a shallow clone without tags).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
FROM_TAG = "v0.10.1"
LEGACY_TAG = "v0.9.1"


def _tags() -> set[str]:
    out = subprocess.run(["git", "tag", "--list"], cwd=REPO, capture_output=True, text=True, check=False)
    return set(out.stdout.split())


@pytest.fixture(scope="module")
def result(tmp_path_factory: pytest.TempPathFactory) -> subprocess.CompletedProcess:
    if not {FROM_TAG, LEGACY_TAG} <= _tags():
        pytest.skip(f"tags {FROM_TAG}/{LEGACY_TAG} not available in {REPO}")
    work = tmp_path_factory.mktemp("compat")
    return subprocess.run(
        [sys.executable, str(HERE / "run_upgrade_compat.py"), "--from", FROM_TAG, "--to", "working-tree",
         "--remote", str(REPO), "--legacy-from", LEGACY_TAG, "--workdir", str(work)],
        capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL, check=False)


def test_runner_exits_zero_on_all_four_projects(result: subprocess.CompletedProcess) -> None:
    assert result.returncode == 0, result.stdout + result.stderr
    assert "4/4 projects pass" in result.stdout


@pytest.mark.parametrize("label", ["(i) new project", "(ii) third-party features/", "(iii) mid-cycle", "(iv) archive shape"])
def test_each_project_reports_pass(result: subprocess.CompletedProcess, label: str) -> None:
    assert any(line.startswith("PASS") and label in line for line in result.stdout.splitlines()), result.stdout


def test_second_upgrade_is_a_no_op_in_every_project(result: subprocess.CompletedProcess) -> None:
    assert result.stdout.count("second upgrade: 'Harness already up to date at") == 3
    assert result.stdout.count("empty diff") >= 4


def test_plugin_is_updated_only_where_installed(result: subprocess.CompletedProcess) -> None:
    assert "plugin: not installed; not created" in result.stdout  # (i)
    assert "plugin: updated" in result.stdout  # (ii)
    assert "plugin: refused (edited by hand)" in result.stdout  # (iv)


def test_no_tag_was_created_in_the_real_repository(result: subprocess.CompletedProcess) -> None:
    assert "v0.11.0" not in _tags()


def test_seja_version_and_changelog_agree() -> None:
    """.seja-version names the version of the top release heading of CHANGELOG.md (the real version files)."""
    version = (REPO / ".seja-version").read_text(encoding="utf-8").strip()
    headings = [line for line in (REPO / "CHANGELOG.md").read_text(encoding="utf-8").splitlines()
                if line.startswith("## [v")]
    assert headings and headings[0].startswith(f"## [{version}]"), (version, headings[:1])

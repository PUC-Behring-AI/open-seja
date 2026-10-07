"""Tests for reserve_id.py (plan-000019 Step 2): ULID identity and birth record."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from artifact_id import ARTIFACT_ID_RE, is_ulid_id, visible_id

SCRIPT = Path(__file__).resolve().parent.parent / "reserve_id.py"

_INDEX = """\
# Artifact Index

| Date | Type | ID | Title | Status | File |
|------|------|----|-------|--------|------|
| 2026-10-01 | plan | 000007 | Old plan | DONE | plans/plan-000007-old.md |
"""

_SECRET_NAME = "Fulano Distinto Sobrenome"


def _env(tmp_path: Path) -> dict:
    gitcfg = tmp_path / "gitconfig"
    gitcfg.write_text(
        f"[user]\n\tname = {_SECRET_NAME}\n\temail = dev@example.org\n",
        encoding="utf-8",
    )
    env = dict(os.environ)
    env["GIT_CONFIG_GLOBAL"] = str(gitcfg)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def _run(tmp_path: Path, out: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", str(out), *args],
        capture_output=True,
        text=True,
        env=_env(tmp_path),
        cwd=str(tmp_path),
        check=False,
    )


def _make_output(base: Path) -> Path:
    out = base / "_output"
    out.mkdir(parents=True)
    (out / "INDEX.md").write_text(_INDEX, encoding="utf-8")
    return out


def _ids(out: Path) -> list[Path]:
    d = out / "ids"
    return sorted(d.glob("*.json")) if d.is_dir() else []


def test_two_copies_reserve_distinct_ids(tmp_path: Path) -> None:
    a = _make_output(tmp_path / "a")
    b = tmp_path / "b" / "_output"
    shutil.copytree(a, b)
    ra = _run(tmp_path, a, "--type", "plan", "--title", "t")
    rb = _run(tmp_path, b, "--type", "plan", "--title", "t")
    assert ra.returncode == 0, ra.stderr
    assert rb.returncode == 0, rb.stderr
    id_a, id_b = ra.stdout.strip(), rb.stdout.strip()
    assert id_a != id_b
    uid_a = json.loads(_ids(a)[0].read_text(encoding="utf-8"))["uid"]
    uid_b = json.loads(_ids(b)[0].read_text(encoding="utf-8"))["uid"]
    assert uid_a != uid_b


def test_reserve_writes_one_birth_record_and_leaves_index_alone(tmp_path: Path) -> None:
    out = _make_output(tmp_path)
    index = out / "INDEX.md"
    before = index.read_text(encoding="utf-8")
    mtime = index.stat().st_mtime_ns
    r = _run(tmp_path, out, "--type", "plan", "--title", "Meu plano")
    assert r.returncode == 0, r.stderr
    vid = r.stdout.strip()
    assert ARTIFACT_ID_RE.match(vid) and not vid.isdigit()
    files = _ids(out)
    assert len(files) == 1
    rec = json.loads(files[0].read_text(encoding="utf-8"))
    assert files[0].name == f"{rec['uid']}.json"
    for key in ("schema_version", "type", "title", "author", "ts_utc"):
        assert key in rec
    assert rec["type"] == "plan"
    assert rec["title"] == "Meu plano"
    assert rec["id"] == vid == visible_id(rec["uid"])
    assert f"uid: {rec['uid']}" in r.stderr
    assert index.read_text(encoding="utf-8") == before
    assert index.stat().st_mtime_ns == mtime


def test_dry_run_creates_nothing(tmp_path: Path) -> None:
    out = tmp_path / "_output"
    r = _run(tmp_path, out, "--type", "plan", "--title", "t", "--dry-run")
    assert r.returncode == 0, r.stderr
    vid = r.stdout.strip()
    assert ARTIFACT_ID_RE.match(vid) and not vid.isdigit()
    assert not out.exists()


def test_json_output(tmp_path: Path) -> None:
    out = _make_output(tmp_path)
    r = _run(tmp_path, out, "--type", "research", "--title", "t", "--json")
    assert r.returncode == 0, r.stderr
    rec = json.loads(r.stdout)
    assert is_ulid_id(rec["id"])
    assert rec["id"] == visible_id(rec["uid"])
    assert (out / "ids" / f"{rec['uid']}.json").is_file()


def test_valid_origin_is_recorded(tmp_path: Path) -> None:
    out = _make_output(tmp_path)
    r = _run(tmp_path, out, "--type", "plan", "--title", "t", "--origin", "research-20261006-q8zrj4")
    assert r.returncode == 0, r.stderr
    rec = json.loads(_ids(out)[0].read_text(encoding="utf-8"))
    assert rec["origin"] == "research-20261006-q8zrj4"


@pytest.mark.parametrize("origin", ["foo", "research-", "research-0007", "Plan-000007"])
def test_invalid_origin_exits_2_without_files(tmp_path: Path, origin: str) -> None:
    out = _make_output(tmp_path)
    r = _run(tmp_path, out, "--type", "plan", "--title", "t", "--origin", origin)
    assert r.returncode == 2
    assert _ids(out) == []


def test_default_author_never_contains_user_name(tmp_path: Path) -> None:
    out = _make_output(tmp_path)
    r = _run(tmp_path, out, "--type", "plan", "--title", "t", "--json")
    assert r.returncode == 0, r.stderr
    raw = _ids(out)[0].read_text(encoding="utf-8")
    assert _SECRET_NAME not in raw
    assert "Fulano" not in raw
    rec = json.loads(raw)
    assert len(rec["author"]) == 12
    int(rec["author"], 16)


@pytest.mark.parametrize("author", ["0123456789ab", "unknown"])
def test_explicit_author_overrides_default(tmp_path: Path, author: str) -> None:
    out = _make_output(tmp_path)
    r = _run(tmp_path, out, "--type", "plan", "--title", "t", "--author", author, "--json")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["author"] == author


@pytest.mark.parametrize(
    "author",
    [
        "dev-a",
        _SECRET_NAME,
        "0123456789AB",
        "0123456789a",
        "0123456789abc",
        "0123456789ab\n",
        "unknown\n",
        "",
    ],
)
def test_free_text_author_exits_2_without_files(tmp_path: Path, author: str) -> None:
    out = _make_output(tmp_path)
    r = _run(tmp_path, out, "--type", "plan", "--title", "t", "--author", author)
    assert r.returncode == 2
    assert "--author" in r.stderr
    assert _SECRET_NAME not in r.stderr
    assert _ids(out) == []


def test_origin_with_trailing_newline_exits_2(tmp_path: Path) -> None:
    out = _make_output(tmp_path)
    r = _run(tmp_path, out, "--type", "plan", "--title", "t", "--origin", "research-000018\n")
    assert r.returncode == 2
    assert _ids(out) == []

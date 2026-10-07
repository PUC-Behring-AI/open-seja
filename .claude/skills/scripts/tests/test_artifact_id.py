"""Tests for artifact_id.py (plan-000019 Step 1)."""
from __future__ import annotations

import hashlib
import re
import subprocess
from datetime import datetime, timezone

import artifact_id
import pytest
from artifact_id import (
    ARTIFACT_ID,
    ARTIFACT_ID_RE,
    birth_record,
    default_author,
    is_legacy_id,
    is_ulid_id,
    new_ulid,
    normalize_id,
    ulid_timestamp,
    visible_id,
)

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _encode_ts(ms: int) -> str:
    out = []
    for _ in range(10):
        out.append(_CROCKFORD[ms & 31])
        ms >>= 5
    return "".join(reversed(out))


def _ulid_at(dt: datetime, rand: str = "ABCDEFGHJKMNPQRS") -> str:
    return _encode_ts(int(dt.timestamp() * 1000)) + rand


# --- new_ulid ---------------------------------------------------------------


def test_new_ulid_10000_calls_are_26_chars_and_distinct():
    ids = [new_ulid() for _ in range(10_000)]
    assert all(len(u) == 26 for u in ids)
    assert all(set(u) <= set(_CROCKFORD) for u in ids)
    assert len(set(ids)) == len(ids)


def test_new_ulid_two_ms_apart_sort_lexicographically(monkeypatch):
    base = 1_791_417_599_000 * 1_000_000  # ns
    clock = iter([base, base + 2_000_000])
    monkeypatch.setattr(artifact_id.time, "time_ns", lambda: next(clock))
    first = new_ulid()
    second = new_ulid()
    assert first < second
    assert first[:10] < second[:10]


# --- ulid_timestamp / visible_id ------------------------------------------


def test_visible_id_and_timestamp_at_end_of_day():
    instant = datetime(2026, 10, 7, 23, 59, 59, tzinfo=timezone.utc)
    uid = _ulid_at(instant, rand="0000000000K3M9QZ")
    assert visible_id(uid) == "20261007-k3m9qz"
    assert visible_id(uid) == "20261007-" + uid[-6:].lower()
    assert ulid_timestamp(uid) == instant
    assert ulid_timestamp(uid).tzinfo is not None


def test_visible_id_of_generated_ulid_matches_grammar():
    vid = visible_id(new_ulid())
    assert ARTIFACT_ID_RE.match(vid)
    assert is_ulid_id(vid)


def test_ulid_timestamp_rejects_invalid():
    with pytest.raises(ValueError):
        ulid_timestamp("not-a-ulid")


# --- normalize_id ---------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("7", "000007"),
        ("000007", "000007"),
        ("123456", "123456"),
        ("20261007-k3m9qz", "20261007-k3m9qz"),
        ("1234567", "1234567"),
    ],
)
def test_normalize_id(raw, expected):
    assert normalize_id(raw) == expected


# --- regexes ----------------------------------------------------------------


@pytest.mark.parametrize("value", ["000007", "20261007-k3m9qz"])
def test_artifact_id_re_matches(value):
    assert ARTIFACT_ID_RE.match(value)


@pytest.mark.parametrize("value", ["0007", "20261007-K3M9QZ", "20261007-k3m9", "", "0000007"])
def test_artifact_id_re_rejects(value):
    assert not ARTIFACT_ID_RE.match(value)


@pytest.mark.parametrize("value", ["000007\n", "20261007-k3m9qz\n"])
def test_artifact_id_re_rejects_trailing_newline(value):
    assert not ARTIFACT_ID_RE.match(value)
    assert not is_legacy_id(value)
    assert not is_ulid_id(value)


def test_ulid_timestamp_rejects_trailing_newline():
    uid = _ulid_at(datetime(2026, 10, 7, tzinfo=timezone.utc))
    ulid_timestamp(uid)
    with pytest.raises(ValueError):
        ulid_timestamp(uid + "\n")


def test_artifact_id_has_no_capture_groups():
    assert re.compile(ARTIFACT_ID).groups == 0


def test_is_legacy_and_is_ulid():
    assert is_legacy_id("000007")
    assert not is_legacy_id("20261007-k3m9qz")
    assert is_ulid_id("20261007-k3m9qz")
    assert not is_ulid_id("000007")


# --- birth_record ---------------------------------------------------------


def test_birth_record_fields():
    rec = birth_record("plan", "Some title", "abc123def456", "research-000018")
    assert rec["schema_version"] == 1
    assert len(rec["uid"]) == 26
    assert rec["id"] == visible_id(rec["uid"])
    assert rec["ts_utc"] == ulid_timestamp(rec["uid"]).isoformat()
    assert rec["type"] == "plan"
    assert rec["title"] == "Some title"
    assert rec["author"] == "abc123def456"
    assert rec["origin"] == "research-000018"


def test_birth_record_defaults(monkeypatch):
    monkeypatch.setattr(artifact_id, "default_author", lambda: "feedbeef0001")
    rec = birth_record("research", "T", None, None)
    assert rec["author"] == "feedbeef0001"
    assert rec["origin"] is None


# --- default_author -------------------------------------------------------


def _fake_git(email: str | None, name: str):
    def run(cmd, *args, **kwargs):
        key = cmd[-1]
        if key == "user.email":
            if email is None:
                return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout=email + "\n", stderr="")
        if key == "user.name":
            return subprocess.CompletedProcess(cmd, 0, stdout=name + "\n", stderr="")
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="")

    return run


def test_default_author_is_email_hash_never_name(monkeypatch):
    monkeypatch.setattr(artifact_id.subprocess, "run", _fake_git("dev@example.org", "Ana Silva"))
    author = default_author()
    assert re.fullmatch(r"[0-9a-f]{12}", author)
    assert author == hashlib.sha256(b"dev@example.org").hexdigest()[:12]
    assert "Ana" not in author and "Silva" not in author


def test_default_author_falls_back_to_user(monkeypatch):
    monkeypatch.setattr(artifact_id.subprocess, "run", _fake_git(None, "Ana Silva"))
    monkeypatch.setenv("USER", "asilva")
    assert default_author() == hashlib.sha256(b"asilva").hexdigest()[:12]


def test_default_author_unknown_when_nothing(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("git")

    monkeypatch.setattr(artifact_id.subprocess, "run", boom)
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("USERNAME", raising=False)
    assert default_author() == "unknown"

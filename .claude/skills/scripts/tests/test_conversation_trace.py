"""Tests for conversation_trace.py (list)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import conversation_trace  # noqa: E402


def _write_trace(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def _row(n: int, session: str, emitter: str, skill: str | None) -> dict:
    return {"evt_id": f"qa-{n:06d}", "session_id": session, "emitter": emitter,
            "message": f"m{n}", "led_to_skill": skill, "timestamp": "2026-10-07T10:00:00+00:00"}


def test_list_filters_by_session_and_skill_in_order(tmp_path):
    trace = tmp_path / "t.jsonl"
    _write_trace(trace, [
        _row(1, "s1", "user", "plan X"),
        _row(2, "s1", "user", "implement Y"),
        _row(3, "s2", "user", "plan X"),
        _row(4, "s1", "user", "plan X"),
    ])
    got = conversation_trace.list_entries("s1", led_to_skill="plan X", trace_file=trace)
    assert [e["evt_id"] for e in got] == ["qa-000001", "qa-000004"]


def test_list_since_evt_and_no_rewrite(tmp_path):
    trace = tmp_path / "t.jsonl"
    _write_trace(trace, [_row(1, "s1", "user", None), _row(2, "s1", "claude", None),
                         _row(3, "s1", "user", None)])
    before = trace.read_bytes()
    got = conversation_trace.list_entries("s1", since_evt="qa-000001", trace_file=trace)
    assert [e["evt_id"] for e in got] == ["qa-000002", "qa-000003"]
    assert trace.read_bytes() == before


def test_list_missing_file_is_empty(tmp_path):
    assert conversation_trace.list_entries("s1", trace_file=tmp_path / "nope.jsonl") == []


def _chain(n: int, emitter: str, skill: str | None, prev: int | None, session: str = "s1") -> dict:
    row = _row(n, session, emitter, skill)
    row["preceding_evt_id"] = f"qa-{prev:06d}" if prev else "null"
    return row


def test_exchange_users_come_from_tagged_claude_entry(tmp_path):
    trace = tmp_path / "t.jsonl"
    _write_trace(trace, [
        _chain(1, "user", None, None), _chain(2, "claude", None, 1),
        _chain(3, "user", None, 2), _chain(4, "user", None, 3),
        _chain(5, "claude", "plan X", 4),
    ])
    got = conversation_trace.exchange_user_entries("s1", "/plan X", trace_file=trace)
    assert [e["evt_id"] for e in got] == ["qa-000003", "qa-000004"]


def test_exchange_two_skills_do_not_leak(tmp_path):
    trace = tmp_path / "t.jsonl"
    _write_trace(trace, [
        _chain(1, "user", None, None), _chain(2, "claude", "plan X", 1),
        _chain(3, "user", None, 2), _chain(4, "claude", "implement Y", 3),
    ])
    plan = conversation_trace.exchange_user_entries("s1", "plan X", trace_file=trace)
    impl = conversation_trace.exchange_user_entries("s1", "implement Y", trace_file=trace)
    assert [e["evt_id"] for e in plan] == ["qa-000001"]
    assert [e["evt_id"] for e in impl] == ["qa-000003"]


def test_exchange_untagged_is_empty_and_user_tag_still_counts(tmp_path):
    trace = tmp_path / "t.jsonl"
    _write_trace(trace, [_chain(1, "user", None, None), _chain(2, "claude", None, 1)])
    assert conversation_trace.exchange_user_entries("s1", "plan X", trace_file=trace) == []
    _write_trace(trace, [_chain(1, "user", "plan X", None)])
    got = conversation_trace.exchange_user_entries("s1", "plan X", trace_file=trace)
    assert [e["evt_id"] for e in got] == ["qa-000001"]


def test_exchange_since_evt_and_session_filter(tmp_path):
    trace = tmp_path / "t.jsonl"
    _write_trace(trace, [
        _chain(1, "user", None, None), _chain(2, "user", None, 1),
        _chain(3, "claude", "plan X", 2), _chain(4, "user", None, None, "s2"),
    ])
    got = conversation_trace.exchange_user_entries(
        "s1", "plan X", since_evt="qa-000001", trace_file=trace)
    assert [e["evt_id"] for e in got] == ["qa-000002"]

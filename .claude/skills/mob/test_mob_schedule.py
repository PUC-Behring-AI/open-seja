#!/usr/bin/env python3
"""Tests for mob_schedule.py (deterministic /mob session agenda).

Invocation: test
Lifecycle: active

Covers the phase split (proportional and explicit minutes), half-up
rounding with the remainder absorbed by BUILD, slack/reserve arithmetic,
driver rotations, validation errors (exit code 2) and the JSON/markdown
outputs (ISO 8601 with timezone offset on every instant).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import mob_schedule

SCRIPT = Path(__file__).parent / "mob_schedule.py"
TZ = timezone(timedelta(hours=-3))
START = datetime(2026, 9, 26, 14, 0, tzinfo=TZ)


def _build(**overrides):
    params = {
        "duration": None,
        "slot": 90,
        "split": (20, 60, 20),
        "phase_minutes": {},
        "opening": 5,
        "closing": 5,
        "rotation": 10,
        "start": START,
    }
    params.update(overrides)
    return mob_schedule.build_schedule(**params)


def _work_minutes(schedule) -> dict[str, int]:
    return {
        p.name: p.minutes
        for p in schedule.phases
        if p.name in ("PLAN", "BUILD", "REFLECT")
    }


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Phase split
# ---------------------------------------------------------------------------


def test_defaults_with_slot_90():
    schedule = _build()
    assert _work_minutes(schedule) == {"PLAN": 15, "BUILD": 45, "REFLECT": 15}
    assert schedule.slack == 15
    assert schedule.reserve == 5


def test_duration_60_slot_120():
    schedule = _build(duration=60, slot=120)
    assert sum(_work_minutes(schedule).values()) == 60
    assert schedule.slack == 60


def test_half_up_rounding_remainder_goes_to_build():
    schedule = _build(duration=77, slot=90)
    assert _work_minutes(schedule) == {"PLAN": 15, "BUILD": 47, "REFLECT": 15}


def test_half_up_not_bankers_rounding():
    schedule = _build(split=(25, 50, 25), duration=90, slot=120)
    assert _work_minutes(schedule) == {"PLAN": 23, "BUILD": 44, "REFLECT": 23}


def test_explicit_plan_rest_proportional():
    schedule = _build(phase_minutes={"PLAN": 10}, duration=75, slot=90)
    assert _work_minutes(schedule) == {"PLAN": 10, "BUILD": 49, "REFLECT": 16}
    sources = {p.name: p.source for p in schedule.phases}
    assert sources["PLAN"] == "explicit"
    assert sources["BUILD"] == "proportional"
    assert sources["REFLECT"] == "proportional"


def test_all_explicit_without_duration_sums():
    schedule = _build(phase_minutes={"PLAN": 10, "BUILD": 50, "REFLECT": 20}, slot=90)
    assert schedule.duration == 80
    assert _work_minutes(schedule) == {"PLAN": 10, "BUILD": 50, "REFLECT": 20}


def test_timeline_is_contiguous_and_fills_slot():
    schedule = _build()
    names = [p.name for p in schedule.phases]
    assert names == ["OPENING", "PLAN", "BUILD", "REFLECT", "RESERVE", "CLOSING"]
    assert schedule.phases[0].start == START
    for prev, nxt in zip(schedule.phases, schedule.phases[1:]):
        assert prev.end == nxt.start
    assert schedule.phases[-1].end == START + timedelta(minutes=90)


# ---------------------------------------------------------------------------
# Rotations
# ---------------------------------------------------------------------------


def test_rotations_every_10_min_in_build_of_45():
    schedule = _build()
    build = next(p for p in schedule.phases if p.name == "BUILD")
    offsets = [(r - build.start) for r in schedule.rotations]
    assert offsets == [timedelta(minutes=m) for m in (10, 20, 30, 40)]


# ---------------------------------------------------------------------------
# Validation (library raises, CLI exits 2)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "args",
    [
        ["--plan-min", "40", "--build-min", "35", "--duration", "75"],
        ["--plan-min", "50", "--build-min", "50", "--duration", "75"],
        ["--duration", "130", "--slot", "120"],
        ["--duration", "85", "--slot", "90"],
        ["--split", "30/30/30"],
        ["--plan-min", "10", "--build-min", "50", "--reflect-min", "20", "--duration", "75"],
        ["--rotation", "0"],
        ["--drivers", " , "],
    ],
)
def test_invalid_inputs_exit_2(args):
    result = _run_cli(*args, "--format", "json")
    assert result.returncode == 2
    assert result.stderr.strip()
    assert result.stdout == ""


def test_library_raises_schedule_error():
    with pytest.raises(mob_schedule.ScheduleError):
        _build(duration=130, slot=120)


# ---------------------------------------------------------------------------
# Output formats
# ---------------------------------------------------------------------------


def test_json_has_offset_on_every_instant_and_drivers():
    result = _run_cli("--slot", "90", "--start", "14:00", "--drivers", "Ana,João,Zé", "--format", "json")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    instants = [data["start"], data["end"], *data["rotations"]]
    for phase in data["phases"]:
        assert set(phase) >= {"name", "start", "end", "minutes", "source"}
        instants += [phase["start"], phase["end"]]
    for instant in instants:
        parsed = datetime.fromisoformat(instant)
        assert parsed.tzinfo is not None
        assert instant[-6] in "+-" and instant[-3] == ":"
    assert data["slack"] == 15
    assert data["reserve"] == 5
    assert data["drivers"] == ["Ana", "João", "Zé"]
    assert data["phases"][0]["start"].startswith(datetime.now().astimezone().strftime("%Y-%m-%d") + "T14:00:00")


def test_json_omits_drivers_when_not_given():
    result = _run_cli("--format", "json")
    assert result.returncode == 0, result.stderr
    assert "drivers" not in json.loads(result.stdout)


def test_markdown_table_with_clock_times():
    result = _run_cli("--slot", "90", "--start", "14:00", "--format", "md")
    assert result.returncode == 0, result.stderr
    out = result.stdout
    assert "| PLAN | 14:05 | 14:20 | 15 |" in out
    assert "| BUILD | 14:20 | 15:05 | 45 |" in out
    assert "| REFLECT | 15:05 | 15:20 | 15 |" in out
    assert "Slack: 15 min" in out


# ---------------------------------------------------------------------------
# --start parsing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("text", "hour", "minute"), [("14:00", 14, 0), ("9:05", 9, 5),
                                                      ("23:59", 23, 59), (" 07:30 ", 7, 30)])
def test_start_valid_keeps_local_offset(text, hour, minute):
    now = datetime(2026, 9, 26, 11, 37, 42, 123, tzinfo=TZ)
    parsed = mob_schedule._parse_start(text, now)
    assert (parsed.hour, parsed.minute, parsed.second, parsed.microsecond) == (hour, minute, 0, 0)
    assert parsed.date() == now.date()
    assert parsed.utcoffset() == TZ.utcoffset(None)


def test_start_default_is_now_with_seconds_zeroed():
    now = datetime(2026, 9, 26, 11, 37, 42, tzinfo=TZ)
    assert mob_schedule._parse_start(None, now) == datetime(2026, 9, 26, 11, 37, tzinfo=TZ)


def test_start_cli_keeps_local_offset():
    result = _run_cli("--start", "14:00", "--format", "json")
    assert result.returncode == 0, result.stderr
    start = datetime.fromisoformat(json.loads(result.stdout)["start"])
    local_offset = datetime.now().astimezone().replace(hour=14, minute=0).utcoffset()
    assert start.utcoffset() == local_offset
    assert (start.hour, start.minute) == (14, 0)


@pytest.mark.parametrize("text", ["24:00", "14:60", "14h00", "1400", "abc", "14:5", ""])
def test_start_invalid_exits_2(text):
    result = _run_cli("--start", text, "--format", "json")
    assert result.returncode == 2
    assert "--start" in result.stderr
    assert result.stdout == ""

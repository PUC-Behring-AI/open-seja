#!/usr/bin/env python3
"""Tests for mob_timer.py (/mob session timer with JSONL log and status query).

Invocation: test
Lifecycle: active

Uses a fake clock (injectable now/sleep) so no test waits in real time.
Agendas come from mob_schedule.py, the same generator the skill uses.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import mob_schedule
import mob_timer

SCRIPT = Path(__file__).parent / "mob_timer.py"
TZ = timezone(timedelta(hours=-3))
START = datetime(2026, 9, 26, 14, 0, tzinfo=TZ)


def _agenda(drivers=None, **overrides) -> dict:
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
    return mob_schedule.schedule_to_dict(mob_schedule.build_schedule(**params), drivers)


class FakeClock:
    def __init__(self, start: datetime, on_sleep=None):
        self.t = start
        self.sleeps: list[float] = []
        self.on_sleep = on_sleep

    def now(self) -> datetime:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.t += timedelta(seconds=seconds)
        if self.on_sleep is not None:
            self.on_sleep(self)


def _run(agenda, tmp_path, clock, **kwargs):
    log = tmp_path / "timer.jsonl"
    out = StringIO()
    code = mob_timer.run_timer(agenda, log, clock.now, clock.sleep, out, **kwargs)
    return code, out.getvalue().splitlines(), _read_log(log)


def _read_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _events(log):
    return [r for r in log if r["type"] not in ("started",)]


# ---------------------------------------------------------------------------
# run: order, log, types
# ---------------------------------------------------------------------------


def test_events_in_order_and_logged_with_utc_and_types(tmp_path):
    clock = FakeClock(START)
    code, lines, log = _run(_agenda(), tmp_path, clock)
    assert code == 0
    events = _events(log)
    scheduled = [datetime.fromisoformat(r["scheduled"]) for r in events]
    assert scheduled == sorted(scheduled)
    allowed = {"phase_start", "phase_warning", "driver_change", "phase_end", "ended"}
    assert {r["type"] for r in events} <= allowed
    for record in log:
        ts = datetime.fromisoformat(record["ts"])
        assert ts.utcoffset() == timedelta(0)
    assert events[0]["type"] == "phase_start" and events[0]["phase"] == "OPENING"
    assert events[-1]["type"] == "ended"
    assert events[-1]["reason"] == "completed"
    # one stdout line per event, format HH:MM | PHASE | text
    assert len(lines) == len(events)
    assert lines[0].startswith("14:00 | OPENING | ")
    assert all(len(line.split(" | ")) == 3 for line in lines)


def test_display_label_separate_from_data(tmp_path):
    clock = FakeClock(START)
    _, _, log = _run(_agenda(), tmp_path, clock)
    for record in _events(log):
        assert "display" in record
        assert record["type"] not in record["display"] or record["type"] == "ended"


def test_log_timestamps_follow_the_real_clock(tmp_path):
    clock = FakeClock(START)
    _, _, log = _run(_agenda(), tmp_path, clock)
    build_start = next(r for r in log if r["type"] == "phase_start" and r["phase"] == "BUILD")
    assert datetime.fromisoformat(build_start["ts"]) == datetime.fromisoformat(
        build_start["scheduled"]
    )


# ---------------------------------------------------------------------------
# warnings
# ---------------------------------------------------------------------------


def test_warning_5_min_before_build_end_and_2_min_before_others(tmp_path):
    agenda = _agenda()
    clock = FakeClock(START)
    _, _, log = _run(agenda, tmp_path, clock)
    ends = {p["name"]: datetime.fromisoformat(p["end"]) for p in agenda["phases"]}
    warnings = {r["phase"]: datetime.fromisoformat(r["scheduled"])
                for r in log if r["type"] == "phase_warning"}
    assert warnings["BUILD"] == ends["BUILD"] - timedelta(minutes=5)
    assert warnings["PLAN"] == ends["PLAN"] - timedelta(minutes=2)
    assert warnings["REFLECT"] == ends["REFLECT"] - timedelta(minutes=2)
    # slack phases carry no warning
    assert not {"OPENING", "RESERVE", "CLOSING"} & set(warnings)


def test_warning_omitted_in_a_1_minute_phase(tmp_path):
    agenda = _agenda(phase_minutes={"PLAN": 1}, duration=75)
    clock = FakeClock(START)
    _, _, log = _run(agenda, tmp_path, clock)
    assert not [r for r in log if r["type"] == "phase_warning" and r["phase"] == "PLAN"]
    assert [r for r in log if r["type"] == "phase_warning" and r["phase"] == "BUILD"]


# ---------------------------------------------------------------------------
# drivers
# ---------------------------------------------------------------------------


def test_driver_change_names_next_driver_circularly_utf8(tmp_path):
    agenda = _agenda(drivers=["Ana", "Joao", "Ines"], rotation=10)
    clock = FakeClock(START)
    _, _, log = _run(agenda, tmp_path, clock)
    build_start = next(r for r in log if r["type"] == "phase_start" and r["phase"] == "BUILD")
    assert build_start["driver"] == "Ana"
    changes = [r for r in log if r["type"] == "driver_change"]
    assert len(changes) == len(agenda["rotations"]) == 4
    assert [r["driver"] for r in changes] == ["Joao", "Ines", "Ana", "Joao"]
    assert [r["previous_driver"] for r in changes] == ["Ana", "Joao", "Ines", "Ana"]


def test_driver_change_with_accented_name(tmp_path):
    agenda = _agenda(drivers=["Ana", "Joao", "Inês"])
    clock = FakeClock(START)
    _, lines, _ = _run(agenda, tmp_path, clock)
    raw = (tmp_path / "timer.jsonl").read_text(encoding="utf-8")
    assert "Inês" in raw  # ensure_ascii=False: real UTF-8 in the log
    assert any("Inês" in line for line in lines if "BUILD" in line)


def test_no_driver_events_without_drivers(tmp_path):
    clock = FakeClock(START)
    _, _, log = _run(_agenda(), tmp_path, clock)
    assert not [r for r in log if r["type"] == "driver_change"]


# ---------------------------------------------------------------------------
# rebase, speed, dry-run
# ---------------------------------------------------------------------------


def test_rebase_now_shifts_every_event_by_the_same_offset(tmp_path):
    agenda = _agenda()
    late = START + timedelta(minutes=17, seconds=30)
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    _, _, plain = _run(agenda, tmp_path / "a", FakeClock(START))
    clock = FakeClock(late)
    _, _, rebased = _run(agenda, tmp_path / "b", clock, rebase_now=True)
    started = [r for r in rebased if r["type"] == "started"]
    assert started and started[0]["rebase_offset_seconds"] == 17 * 60 + 30
    a = [datetime.fromisoformat(r["scheduled"]) for r in _events(plain)]
    b = [datetime.fromisoformat(r["scheduled"]) for r in _events(rebased)]
    assert len(a) == len(b)
    assert {y - x for x, y in zip(a, b)} == {timedelta(minutes=17, seconds=30)}
    # nothing fires immediately in catch-up: the first sleep happens after OPENING start
    assert clock.sleeps and all(s > 0 for s in clock.sleeps)


def test_speed_60_sleeps_one_sixtieth_of_real_interval(tmp_path):
    agenda = _agenda()
    clock = FakeClock(START)
    _run(agenda, tmp_path, clock, speed=60.0)
    total = (datetime.fromisoformat(agenda["end"]) - START).total_seconds()
    assert sum(clock.sleeps) == pytest.approx(total / 60)
    # first wait: OPENING start -> OPENING end (5 agenda-minutes) / 60
    assert clock.sleeps[0] == pytest.approx(5 * 60 / 60)


def test_dry_run_does_not_sleep(tmp_path):
    clock = FakeClock(START)

    def forbidden(_):
        raise AssertionError("sleep called in dry-run")

    out = StringIO()
    log = tmp_path / "timer.jsonl"
    code = mob_timer.run_timer(_agenda(drivers=["A", "B"]), log, clock.now, forbidden, out,
                               dry_run=True)
    assert code == 0
    lines = out.getvalue().splitlines()
    assert lines[0].startswith("14:00 | OPENING")
    assert lines[-1].startswith("15:30 | CLOSING")
    assert not log.exists()


# ---------------------------------------------------------------------------
# termination
# ---------------------------------------------------------------------------


def test_sigterm_logs_ended_and_returns_0(tmp_path):
    def terminate(clock):
        if len(clock.sleeps) == 3:
            signal.raise_signal(signal.SIGTERM)

    clock = FakeClock(START, on_sleep=terminate)
    previous = signal.getsignal(signal.SIGTERM)
    code, _, log = _run(_agenda(), tmp_path, clock)
    assert code == 0
    assert log[-1]["type"] == "ended"
    assert log[-1]["reason"] == "terminated"
    assert signal.getsignal(signal.SIGTERM) == previous


def test_keyboard_interrupt_logs_interrupted_and_returns_130(tmp_path):
    def interrupt(clock):
        if len(clock.sleeps) == 2:
            raise KeyboardInterrupt

    clock = FakeClock(START, on_sleep=interrupt)
    code, _, log = _run(_agenda(), tmp_path, clock)
    assert code == 130
    assert log[-1]["type"] == "interrupted"


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def test_status_mid_build():
    agenda = _agenda(drivers=["Ana", "Joao", "Ines"])
    build = next(p for p in agenda["phases"] if p["name"] == "BUILD")
    build_start = datetime.fromisoformat(build["start"])
    now = build_start + timedelta(minutes=23)
    status = mob_timer.current_status(agenda, now)
    assert status["state"] == "running"
    assert status["phase"] == "BUILD"
    assert status["minutes_remaining"] == pytest.approx(build["minutes"] - 23)
    assert status["driver"] == "Ines"  # rotations at +10 (Joao), +20 (Ines)
    assert status["next_event"]["type"] == "driver_change"
    assert status["next_event"]["driver"] == "Ana"


def test_status_before_start_is_not_started():
    status = mob_timer.current_status(_agenda(), START - timedelta(minutes=3))
    assert status["state"] == "not_started"
    assert status["phase"] is None
    assert status["next_event"]["type"] == "phase_start"
    assert status["minutes_until_start"] == pytest.approx(3)


def test_status_after_end_is_finished():
    status = mob_timer.current_status(_agenda(), START + timedelta(minutes=200))
    assert status["state"] == "finished"
    assert status["next_event"] is None


def test_status_applies_rebase_offset():
    agenda = _agenda()
    offset = timedelta(minutes=10)
    # rebased: OPENING 14:10-14:15, PLAN 14:15-14:30
    status = mob_timer.current_status(agenda, START + timedelta(minutes=22), offset)
    assert status["phase"] == "PLAN"
    assert status["minutes_remaining"] == pytest.approx(8)


def test_status_during_reserve():
    agenda = _agenda()
    # OPENING 0-5, PLAN 5-20, BUILD 20-65, REFLECT 65-80, RESERVE 80-85, CLOSING 85-90
    status = mob_timer.current_status(agenda, START + timedelta(minutes=82))
    assert status["state"] == "running"
    assert status["phase"] == "RESERVE"
    assert status["minutes_remaining"] == pytest.approx(3)
    assert status["driver"] is None
    assert status["next_event"]["type"] == "phase_end"
    assert status["next_event"]["phase"] == "RESERVE"


def test_status_honors_speed_from_the_base():
    agenda = _agenda()
    now = START + timedelta(minutes=1)  # 1 real minute at speed 60 = agenda +60 min
    status = mob_timer.current_status(agenda, now, speed=60)
    assert status["now"] == now.isoformat()  # the real clock is still reported
    assert status["speed"] == 60
    assert status["phase"] == "BUILD"  # BUILD spans +20..+65
    assert status["minutes_remaining"] == pytest.approx(5)
    assert status["next_event"]["type"] == "phase_end"  # the 5-min warning fired at +60


def test_status_with_speed_before_base_is_not_started():
    status = mob_timer.current_status(_agenda(), START - timedelta(minutes=3), speed=60)
    assert status["state"] == "not_started"
    assert status["minutes_until_start"] == pytest.approx(3)


def test_status_with_speed_and_rebase():
    agenda = _agenda()
    offset = timedelta(minutes=10)  # base 14:10
    status = mob_timer.current_status(agenda, START + timedelta(minutes=10, seconds=10),
                                      offset, speed=60)
    assert status["phase"] == "PLAN"  # agenda +10 min: PLAN spans +5..+20
    assert status["minutes_remaining"] == pytest.approx(10)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                          check=False, text=True, encoding="utf-8")


def test_cli_dry_run_and_status_with_log(tmp_path):
    agenda_path = tmp_path / "agenda.json"
    agenda_path.write_text(json.dumps(_agenda(drivers=["Ana", "Inês"]), ensure_ascii=False),
                           encoding="utf-8")
    result = _cli("run", "--agenda", str(agenda_path), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "Inês" in result.stdout
    assert result.stdout.splitlines()[0].startswith("14:00 | OPENING")

    log = tmp_path / "timer.jsonl"
    log.write_text(json.dumps({"type": "started", "rebase_offset_seconds": 600}) + "\n",
                   encoding="utf-8")
    status = _cli("status", "--agenda", str(agenda_path), "--log", str(log))
    assert status.returncode == 0, status.stderr
    data = json.loads(status.stdout)
    assert data["rebase_offset_seconds"] == 600
    assert "state" in data


def test_cli_invalid_agenda_exits_2(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = _cli("status", "--agenda", str(bad))
    assert result.returncode == 2
    assert "mob_timer: error" in result.stderr


def _write_agenda(tmp_path, agenda) -> Path:
    path = tmp_path / "agenda.json"
    path.write_text(json.dumps(agenda, ensure_ascii=False), encoding="utf-8")
    return path


def test_run_records_pid_in_started(tmp_path):
    _, _, log = _run(_agenda(), tmp_path, FakeClock(START))
    assert log[0]["type"] == "started"
    assert log[0]["pid"] == os.getpid()


def test_cli_status_uses_speed_from_started_record(tmp_path):
    agenda_path = _write_agenda(tmp_path, _agenda())
    base = datetime.now().astimezone() - timedelta(seconds=40)  # agenda +40 min at speed 60
    offset = base - START
    log = tmp_path / "timer.jsonl"
    log.write_text(json.dumps({"type": "started", "rebase_offset_seconds": offset.total_seconds(),
                               "speed": 60, "agenda_start": base.isoformat(),
                               "pid": os.getpid()}) + "\n", encoding="utf-8")
    result = _cli("status", "--agenda", str(agenda_path), "--log", str(log))
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["speed"] == 60
    assert data["phase"] == "BUILD"  # BUILD spans +20..+65; tolerant to ~20 s of startup
    assert data["timer"] == "running"


def _dead_pid() -> int:
    proc = subprocess.Popen([sys.executable, "-c", "pass"])
    proc.wait()
    return proc.pid


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX liveness check only")
def test_cli_status_reports_stale_when_timer_pid_is_gone(tmp_path):
    agenda_path = _write_agenda(tmp_path, _agenda())
    log = tmp_path / "timer.jsonl"
    log.write_text(json.dumps({"type": "started", "rebase_offset_seconds": 0, "speed": 1,
                               "pid": _dead_pid()}) + "\n", encoding="utf-8")
    data = json.loads(_cli("status", "--agenda", str(agenda_path), "--log", str(log)).stdout)
    assert data["timer"] == "stale"


def test_cli_status_without_pid_keeps_running(tmp_path):
    agenda_path = _write_agenda(tmp_path, _agenda())
    log = tmp_path / "timer.jsonl"
    log.write_text(json.dumps({"type": "started", "rebase_offset_seconds": 0}) + "\n",
                   encoding="utf-8")
    data = json.loads(_cli("status", "--agenda", str(agenda_path), "--log", str(log)).stdout)
    assert data["timer"] == "running"
    assert data["speed"] == 1

#!/usr/bin/env python3
# designer: When your /mob session is running, I'm the clock the whole group
#   hears: I announce each phase start, warn you before a phase ends (5 min in
#   BUILD so there is time to close the step and run the quality gate), name
#   the next driver at each rotation, and write everything to a log. Whenever
#   the agent needs to know where the session stands, it asks me for the
#   status, computed from the agenda and the clock, not from relayed messages.
"""
mob_timer.py -- timer, JSONL log and status query for a /mob session.

Invocation: skill-invoked, user-cli
Lifecycle: active

Reads the agenda JSON produced by mob_schedule.py (--format json).

`run` sleeps until each event and prints one line per event, flushed at once,
as `HH:MM | <PHASE> | <text>` (HH:MM is the scheduled agenda time in the
agenda's timezone). Events:

- phase_start   every phase (OPENING, PLAN, BUILD, REFLECT, RESERVE, CLOSING);
                BUILD start also names the first driver when `drivers` exist.
- phase_warning PLAN/BUILD/REFLECT only: 5 min before BUILD ends, 2 min before
                PLAN/REFLECT end; omitted when the phase is not longer than the
                warning. The slack phases (OPENING, RESERVE, CLOSING) get none.
- driver_change at each agenda rotation, naming the next driver (circular).
- phase_end     every phase.
- ended         after CLOSING ends (reason "completed", exit 0) or on SIGTERM
                (reason "terminated", exit 0).
- interrupted   on SIGINT / KeyboardInterrupt (exit 130).

Events at the same instant are ordered phase_end, phase_start, driver_change,
phase_warning. Every event is appended to --log as one JSON object per line
(UTF-8): `ts` (real UTC time), `type`, `phase`, `scheduled` (agenda instant,
after rebase), data fields (`driver`, `previous_driver`, `minutes_left`,
`reason`) and a separate human `display` text. The first record is
`{"type": "started", "rebase_offset_seconds": N, "speed": S, "agenda_start",
"pid"}` (agenda_start is the rebased base; pid is the timer process).

--rebase-now shifts the whole agenda so it starts at launch time (durations
kept) and records the shift in the `started` record. --speed N divides every
wait (offsets from the agenda start) by N, for tests and rehearsals. Without
--rebase-now, events already in the past fire immediately (catch-up).
--dry-run prints every event without sleeping or writing the log.

`status` prints JSON computed from agenda + clock (+ the rebase offset, speed
and pid read from the `started` record of --log): state (not_started | running
| finished), phase, minutes_remaining, driver, next_event, speed, and `timer`
(the last lifecycle record in the log: running | ended | interrupted | null;
"stale" when the log says running but the recorded pid no longer exists, POSIX
only). With speed S != 1 the clock is mapped to agenda time as
base + (now - base) * S, so phase, minutes_remaining and next_event are in
agenda minutes while `now` stays the real clock.

Usage
-----
    python .claude/skills/mob/mob_timer.py run --agenda a.json --log t.jsonl --rebase-now
    python .claude/skills/mob/mob_timer.py run --agenda a.json --dry-run
    python .claude/skills/mob/mob_timer.py status --agenda a.json --log t.jsonl

Invalid input exits with code 2 and a message on stderr.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import signal
import sys
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TextIO

WORK_WARNING_MINUTES = {"PLAN": 2, "BUILD": 5, "REFLECT": 2}
EXIT_OK = 0
EXIT_INVALID = 2
EXIT_INTERRUPTED = 130
_ORDER = {"phase_end": 0, "phase_start": 1, "driver_change": 2, "phase_warning": 3}


class TimerError(ValueError):
    """Invalid agenda or arguments (the CLI maps it to exit code 2)."""


class _Terminated(Exception):
    """Raised by the SIGTERM handler to unwind the sleep loop."""


@dataclass(frozen=True)
class Event:
    at: datetime
    type: str
    phase: str
    display: str
    data: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Agenda -> events
# ---------------------------------------------------------------------------


def _parse_instant(text: str) -> datetime:
    try:
        value = datetime.fromisoformat(text)
    except (TypeError, ValueError):
        raise TimerError(f"invalid ISO instant in agenda: {text!r}") from None
    if value.tzinfo is None:
        raise TimerError(f"agenda instant without timezone offset: {text!r}")
    return value


def _phases(agenda: dict, offset: timedelta) -> list[tuple[str, datetime, datetime, int]]:
    try:
        raw = agenda["phases"]
        phases = [(p["name"], _parse_instant(p["start"]) + offset,
                   _parse_instant(p["end"]) + offset, int(p["minutes"])) for p in raw]
    except (KeyError, TypeError) as err:
        raise TimerError(f"agenda is missing phase data ({err}).") from None
    if not phases:
        raise TimerError("agenda has no phases.")
    return phases


def _rotations(agenda: dict, offset: timedelta) -> list[datetime]:
    return [_parse_instant(r) + offset for r in agenda.get("rotations", [])]


def _drivers(agenda: dict) -> list[str]:
    return [str(d) for d in agenda.get("drivers") or []]


def build_events(agenda: dict, offset: timedelta = timedelta(0)) -> list[Event]:
    """Every timer event of the agenda (shifted by `offset`), in chronological order."""
    drivers = _drivers(agenda)
    events: list[Event] = []
    for name, start, end, minutes in _phases(agenda, offset):
        data, text = {}, "start"
        if name == "BUILD" and drivers:
            data = {"driver": drivers[0]}
            text = f"start -- driver: {drivers[0]}"
        events.append(Event(start, "phase_start", name, text, data))
        warn = WORK_WARNING_MINUTES.get(name)
        if warn is not None and minutes > warn:
            events.append(Event(end - timedelta(minutes=warn), "phase_warning", name,
                                f"{warn} min left", {"minutes_left": warn}))
        events.append(Event(end, "phase_end", name, "end"))
    if drivers:
        for index, instant in enumerate(_rotations(agenda, offset), start=1):
            previous, current = drivers[(index - 1) % len(drivers)], drivers[index % len(drivers)]
            events.append(Event(instant, "driver_change", "BUILD",
                                f"driver change: {previous} -> {current}",
                                {"driver": current, "previous_driver": previous}))
    events.sort(key=lambda e: (e.at, _ORDER[e.type]))
    return events


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


def _utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _emit_line(out: TextIO, at: datetime, phase: str, text: str) -> None:
    out.write(f"{at:%H:%M} | {phase} | {text}\n")
    out.flush()


def _append_log(log_path: Path | None, record: dict) -> None:
    if log_path is None:
        return
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _event_record(event: Event, now: datetime) -> dict:
    return {"ts": _utc_iso(now), "type": event.type, "phase": event.phase,
            "scheduled": event.at.isoformat(), **event.data, "display": event.display}


@contextlib.contextmanager
def _sigterm_raises() -> Iterator[None]:
    def handler(_signum, _frame):
        raise _Terminated

    try:
        previous = signal.signal(signal.SIGTERM, handler)
    except ValueError:  # not in the main thread: no handler, run anyway
        yield
        return
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)


def run_timer(
    agenda: dict, log_path: Path | None, now: Callable[[], datetime],
    sleep: Callable[[float], None], out: TextIO, speed: float = 1.0,
    rebase_now: bool = False, dry_run: bool = False,
) -> int:
    """Announce every event of `agenda`; return 0 at the end or on SIGTERM, 130 on SIGINT."""
    if speed <= 0:
        raise TimerError(f"--speed must be positive (got {speed}).")
    agenda_start = _parse_instant(agenda.get("start") or agenda["phases"][0]["start"])
    launch = now()
    offset = launch - agenda_start if rebase_now else timedelta(0)
    events = build_events(agenda, offset)
    base = agenda_start + offset
    # With --speed, agenda offsets from `base` are compressed: event k fires at
    # base + (at_k - base) / speed (base == launch when rebased).
    last_phase = events[-1].phase

    if dry_run:
        for event in events:
            _emit_line(out, event.at, event.phase, event.display)
        _emit_line(out, events[-1].at, last_phase, "session ended")
        return EXIT_OK

    _append_log(log_path, {"ts": _utc_iso(launch), "type": "started",
                           "rebase_offset_seconds": offset.total_seconds(),
                           "speed": speed, "agenda_start": base.isoformat(),
                           "pid": os.getpid()})
    current = events[0]
    try:
        with _sigterm_raises():
            for event in events:
                target = base + (event.at - base) / speed
                delay = (target - now()).total_seconds()
                if delay > 0:
                    sleep(delay)
                current = event
                _emit_line(out, event.at, event.phase, event.display)
                _append_log(log_path, _event_record(event, now()))
    except _Terminated:
        _emit_line(out, now(), current.phase, "session ended (terminated)")
        _append_log(log_path, {"ts": _utc_iso(now()), "type": "ended", "phase": current.phase,
                               "reason": "terminated", "display": "session ended"})
        return EXIT_OK
    except KeyboardInterrupt:
        _emit_line(out, now(), current.phase, "timer interrupted")
        _append_log(log_path, {"ts": _utc_iso(now()), "type": "interrupted",
                               "phase": current.phase, "display": "timer interrupted"})
        return EXIT_INTERRUPTED
    end = events[-1].at
    _emit_line(out, end, last_phase, "session ended")
    _append_log(log_path, {"ts": _utc_iso(now()), "type": "ended", "phase": last_phase,
                           "scheduled": end.isoformat(), "reason": "completed",
                           "display": "session ended"})
    return EXIT_OK


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------


def _minutes(delta: timedelta) -> float:
    return round(delta.total_seconds() / 60, 2)


def current_status(agenda: dict, now: datetime, rebase_offset: timedelta | None = None,
                   speed: float = 1.0) -> dict:
    """Where the session stands at `now`, from agenda + clock (+ rebase offset, speed).

    With speed != 1 (a sped-up `run`), the real clock is mapped to agenda time
    from the (rebased) agenda start: base + (now - base) * speed. Before the
    base the clock is used as is (not_started). `now` in the output stays real.
    """
    offset = rebase_offset or timedelta(0)
    phases = _phases(agenda, offset)
    events = build_events(agenda, offset)
    real_now = now
    base = phases[0][1]
    if speed != 1 and now >= base:
        now = base + (now - base) * speed
    upcoming = next((e for e in events if e.at > now), None)
    next_event = None if upcoming is None else {
        "type": upcoming.type, "phase": upcoming.phase, "at": upcoming.at.isoformat(),
        "in_minutes": _minutes(upcoming.at - now), "display": upcoming.display, **upcoming.data,
    }
    status: dict = {"now": real_now.isoformat(), "state": "running", "phase": None,
                    "phase_end": None, "minutes_remaining": None, "driver": None,
                    "next_event": next_event,
                    "rebase_offset_seconds": offset.total_seconds(), "speed": speed}
    if now < phases[0][1]:
        status.update(state="not_started", minutes_until_start=_minutes(phases[0][1] - now))
        return status
    if now >= phases[-1][2]:
        status["state"] = "finished"
        return status
    name, _start, end, _minutes_total = next(p for p in phases if p[1] <= now < p[2])
    status.update(phase=name, phase_end=end.isoformat(), minutes_remaining=_minutes(end - now))
    drivers = _drivers(agenda)
    if name == "BUILD" and drivers:
        turns = sum(1 for r in _rotations(agenda, offset) if r <= now)
        status["driver"] = drivers[turns % len(drivers)]
        status["driver_index"] = turns % len(drivers)
    return status


@dataclass(frozen=True)
class LogInfo:
    """What `status` needs from the timer log (last `started` record + lifecycle)."""

    offset: timedelta | None = None
    state: str | None = None
    speed: float = 1.0
    pid: int | None = None


def _read_log(log_path: Path | None) -> LogInfo:
    """Rebase offset, speed and pid of the last `started` record, and the last lifecycle state."""
    if log_path is None or not log_path.exists():
        return LogInfo()
    offset, state, speed, pid = None, None, 1.0, None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = record.get("type")
        if kind == "started":
            offset = timedelta(seconds=float(record.get("rebase_offset_seconds") or 0))
            speed = float(record.get("speed") or 1.0)
            raw_pid = record.get("pid")
            pid = int(raw_pid) if isinstance(raw_pid, int) else None
            state = "running"
        elif kind in ("ended", "interrupted"):
            state = kind
    return LogInfo(offset, state, speed, pid)


def _pid_alive(pid: int) -> bool:
    """POSIX liveness probe; on Windows it cannot tell, so it answers True."""
    if sys.platform == "win32":
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _timer_state(info: LogInfo) -> str | None:
    if info.state == "running" and info.pid is not None and not _pid_alive(info.pid):
        return "stale"
    return info.state


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_agenda(path: str) -> dict:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as err:
        raise TimerError(f"cannot read agenda {path}: {err}") from None
    except json.JSONDecodeError as err:
        raise TimerError(f"agenda {path} is not valid JSON: {err}") from None
    if not isinstance(data, dict) or not data.get("phases"):
        raise TimerError(f"agenda {path} has no phases (expected mob_schedule.py JSON).")
    _phases(data, timedelta(0))
    return data


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Timer and status for a /mob session.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="announce events until the agenda ends")
    run.add_argument("--agenda", required=True, help="agenda JSON from mob_schedule.py")
    run.add_argument("--log", default=None, help="JSONL event log (required unless --dry-run)")
    run.add_argument("--rebase-now", action="store_true", help="shift the agenda to start now")
    run.add_argument("--speed", type=float, default=1.0, help="divide every wait by N")
    run.add_argument("--dry-run", action="store_true", help="print all events without sleeping")
    status = sub.add_parser("status", help="print the current session state as JSON")
    status.add_argument("--agenda", required=True)
    status.add_argument("--log", default=None, help="timer log (for the rebase offset)")
    return parser


def _local_now() -> datetime:
    return datetime.now().astimezone()


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    args = _build_parser().parse_args(argv)
    try:
        agenda = _load_agenda(args.agenda)
        log_path = Path(args.log) if args.log else None
        if args.command == "status":
            info = _read_log(log_path)
            result = current_status(agenda, _local_now(), info.offset, info.speed)
            result["timer"] = _timer_state(info)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return EXIT_OK
        if log_path is None and not args.dry_run:
            raise TimerError("run needs --log unless --dry-run is given.")
        return run_timer(agenda, log_path, _local_now, time.sleep, sys.stdout,
                         speed=args.speed, rebase_now=args.rebase_now, dry_run=args.dry_run)
    except TimerError as err:
        print(f"mob_timer: error: {err}", file=sys.stderr)
        return EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())

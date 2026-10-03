#!/usr/bin/env python3
# designer: When a /mob session is about to start, I'm the one who turns the
#   slot you booked and the work duration you chose into a clock-time agenda:
#   opening, PLAN, BUILD, REFLECT, overrun reserve and closing, plus the
#   instants where the driver hands over the keyboard. The arithmetic is
#   deterministic, so the group sees the same agenda the timer will follow.
"""
mob_schedule.py -- deterministic agenda for a /mob (mob programming) session.

Invocation: skill-invoked, user-cli
Lifecycle: active

Computes PLAN/BUILD/REFLECT minutes from a work duration (default 75 min) and
a PLAN/BUILD/REFLECT split (default 20/60/20). Phases given explicit minutes
stay fixed; the rest of the duration is shared by the other phases in
proportion to their split weights, rounded half-up (math.floor(x + 0.5)), with
the rounding difference absorbed by BUILD (or by the last phase without an
explicit value) so the phases sum exactly to the duration. The slack
(slot - duration) becomes opening + overrun reserve + closing. Driver
rotations happen every --rotation minutes inside BUILD (the last turn may be
shorter).

Usage
-----
    python .claude/skills/mob/mob_schedule.py --slot 90 --format md
    python .claude/skills/mob/mob_schedule.py --duration 60 --slot 120 \\
        --plan-min 10 --start 14:00 --drivers "Ana,Joao" --format json

Invalid input exits with code 2 and a message on stderr.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from fractions import Fraction

WORK_PHASES = ("PLAN", "BUILD", "REFLECT")
DEFAULT_DURATION = 75
DEFAULT_SLOT = 90
DEFAULT_SPLIT = (20, 60, 20)
EXIT_INVALID = 2


class ScheduleError(ValueError):
    """Invalid agenda parameters (the CLI maps it to exit code 2)."""


@dataclass(frozen=True)
class Phase:
    name: str
    start: datetime
    end: datetime
    minutes: int
    source: str  # "explicit" | "proportional" for work phases; "slack" otherwise


@dataclass(frozen=True)
class Schedule:
    duration: int
    slot: int
    start: datetime
    end: datetime
    phases: list[Phase]
    rotations: list[datetime]
    slack: int
    reserve: int
    opening: int
    closing: int
    rotation: int
    split: tuple[int, int, int] = field(default=DEFAULT_SPLIT)


def _half_up(value: Fraction) -> int:
    # Half-up on purpose: round() is banker's rounding (22.5 -> 22).
    return math.floor(value + Fraction(1, 2))


def _require_positive(label: str, value: int) -> None:
    if value <= 0:
        raise ScheduleError(f"{label} must be a positive number of minutes (got {value}).")


def _resolve_duration(duration: int | None, phase_minutes: dict[str, int]) -> int:
    """Rule (a): all three explicit and no duration -> their sum; else given or 75."""
    all_explicit = all(name in phase_minutes for name in WORK_PHASES)
    if duration is None:
        return sum(phase_minutes.values()) if all_explicit else DEFAULT_DURATION
    if all_explicit and sum(phase_minutes.values()) != duration:
        raise ScheduleError(
            f"PLAN+BUILD+REFLECT explicit minutes sum to {sum(phase_minutes.values())}, "
            f"but --duration is {duration}; drop --duration or make them match."
        )
    return duration


def _validate_inputs(
    slot: int, split: tuple[int, int, int], phase_minutes: dict[str, int],
    opening: int, closing: int, rotation: int,
) -> None:
    unknown = set(phase_minutes) - set(WORK_PHASES)
    if unknown:
        raise ScheduleError(f"Unknown phase(s) {sorted(unknown)}; use {list(WORK_PHASES)}.")
    if len(split) != 3 or sum(split) != 100:
        raise ScheduleError(f"--split must have three weights summing to 100 (got {split}).")
    for name, weight in zip(WORK_PHASES, split):
        _require_positive(f"split weight for {name}", weight)
    for name, minutes in phase_minutes.items():
        _require_positive(f"--{name.lower()}-min", minutes)
    for label, value in (("--slot", slot), ("--opening", opening),
                         ("--closing", closing), ("--rotation", rotation)):
        _require_positive(label, value)


def _split_minutes(duration: int, split: tuple[int, int, int],
                   phase_minutes: dict[str, int]) -> dict[str, tuple[int, str]]:
    """Rules (b) and (c): fixed explicit phases, proportional rest, half-up rounding."""
    explicit_total = sum(phase_minutes.values())
    if explicit_total > duration:
        raise ScheduleError(
            f"Explicit phase minutes ({explicit_total}) exceed the duration ({duration})."
        )
    free = [name for name in WORK_PHASES if name not in phase_minutes]
    weights = dict(zip(WORK_PHASES, split))
    remainder = duration - explicit_total
    total_weight = sum(weights[name] for name in free)
    absorber = "BUILD" if "BUILD" in free else (free[-1] if free else None)
    result = {name: (phase_minutes[name], "explicit") for name in phase_minutes}
    for name in free:
        if name != absorber:
            share = Fraction(remainder * weights[name], total_weight)
            result[name] = (_half_up(share), "proportional")
    if absorber is not None:
        taken = sum(result[name][0] for name in free if name != absorber)
        result[absorber] = (remainder - taken, "proportional")
    for name in WORK_PHASES:
        if result[name][0] <= 0:
            raise ScheduleError(
                f"{name} would get {result[name][0]} min; lower the explicit minutes "
                f"of the other phases or raise --duration."
            )
    return result


def _timeline(start: datetime, blocks: list[tuple[str, int, str]]) -> list[Phase]:
    phases, cursor = [], start
    for name, minutes, source in blocks:
        if minutes <= 0:
            continue  # an empty reserve is not a phase
        end = cursor + timedelta(minutes=minutes)
        phases.append(Phase(name, cursor, end, minutes, source))
        cursor = end
    return phases


def _rotations(build: Phase, rotation: int) -> list[datetime]:
    """Rule (e): every `rotation` min inside BUILD; the last turn may be shorter."""
    return [build.start + timedelta(minutes=offset)
            for offset in range(rotation, build.minutes, rotation)]


def build_schedule(
    duration: int | None, slot: int, split: tuple[int, int, int],
    phase_minutes: dict[str, int], opening: int, closing: int, rotation: int,
    start: datetime,
) -> Schedule:
    """Compute the agenda. `phase_minutes` keys are PLAN/BUILD/REFLECT; `start` is tz-aware."""
    if start.tzinfo is None:
        raise ScheduleError("start must be timezone-aware.")
    _validate_inputs(slot, split, phase_minutes, opening, closing, rotation)
    duration = _resolve_duration(duration, phase_minutes)
    _require_positive("--duration", duration)
    if duration > slot:
        raise ScheduleError(f"--duration ({duration}) must not exceed --slot ({slot}).")
    slack = slot - duration
    if opening + closing > slack:
        raise ScheduleError(
            f"Opening ({opening}) + closing ({closing}) exceed the slack "
            f"slot - duration = {slack}; shorten them or the duration."
        )
    work = _split_minutes(duration, split, phase_minutes)
    reserve = slack - opening - closing
    blocks = [("OPENING", opening, "slack")]
    blocks += [(name, *work[name]) for name in WORK_PHASES]
    blocks += [("RESERVE", reserve, "slack"), ("CLOSING", closing, "slack")]
    phases = _timeline(start, blocks)
    build = next(p for p in phases if p.name == "BUILD")
    return Schedule(
        duration=duration, slot=slot, start=start, end=phases[-1].end,
        phases=phases, rotations=_rotations(build, rotation), slack=slack,
        reserve=reserve, opening=opening, closing=closing, rotation=rotation,
        split=split,
    )


def schedule_to_dict(schedule: Schedule, drivers: list[str] | None = None) -> dict:
    """JSON-ready dict; every instant is ISO 8601 with a timezone offset."""
    data = {
        "start": schedule.start.isoformat(),
        "end": schedule.end.isoformat(),
        "slot": schedule.slot,
        "duration": schedule.duration,
        "split": list(schedule.split),
        "slack": schedule.slack,
        "opening": schedule.opening,
        "reserve": schedule.reserve,
        "closing": schedule.closing,
        "rotation": schedule.rotation,
        "phases": [
            {"name": p.name, "start": p.start.isoformat(), "end": p.end.isoformat(),
             "minutes": p.minutes, "source": p.source}
            for p in schedule.phases
        ],
        "rotations": [r.isoformat() for r in schedule.rotations],
    }
    if drivers:
        data["drivers"] = drivers
    return data


def render_markdown(schedule: Schedule, drivers: list[str] | None = None) -> str:
    """Clock-time markdown table plus slack and rotation lines."""
    lines = ["| Phase | Start | End | Minutes | Source |",
             "|-------|-------|-----|---------|--------|"]
    for p in schedule.phases:
        lines.append(f"| {p.name} | {p.start:%H:%M} | {p.end:%H:%M} | {p.minutes} | {p.source} |")
    lines.append("")
    lines.append(
        f"Duration: {schedule.duration} min | Slot: {schedule.slot} min | "
        f"Slack: {schedule.slack} min (opening {schedule.opening}, "
        f"reserve {schedule.reserve}, closing {schedule.closing})"
    )
    turns = []
    for index, instant in enumerate(schedule.rotations):
        label = f" -> {drivers[(index + 1) % len(drivers)]}" if drivers else ""
        turns.append(f"{instant:%H:%M}{label}")
    first = f" (first driver: {drivers[0]})" if drivers else ""
    lines.append(f"Driver rotations every {schedule.rotation} min{first}: "
                 + (", ".join(turns) if turns else "none"))
    return "\n".join(lines) + "\n"


def _parse_split(text: str) -> tuple[int, int, int]:
    parts = text.split("/")
    try:
        values = tuple(int(part) for part in parts)
    except ValueError:
        raise ScheduleError(f"--split must look like 20/60/20 (got {text!r}).") from None
    if len(values) != 3:
        raise ScheduleError(f"--split needs exactly three weights (got {text!r}).")
    return values  # type: ignore[return-value]


def _parse_start(text: str | None, now: datetime) -> datetime:
    base = now.replace(second=0, microsecond=0)
    if text is None:
        return base
    match = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", text.strip())
    if match is None:
        raise ScheduleError(f"--start must be HH:MM (got {text!r}).")
    return base.replace(hour=int(match.group(1)), minute=int(match.group(2)))


def _parse_drivers(text: str | None) -> list[str] | None:
    if text is None:
        return None
    names = [name.strip() for name in text.split(",") if name.strip()]
    if not names:
        raise ScheduleError("--drivers must list at least one name, comma-separated.")
    return names


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic agenda for a /mob session.")
    parser.add_argument("--duration", type=int, default=None,
                        help="work minutes (default: sum of explicit phases, else 75)")
    parser.add_argument("--slot", type=int, default=DEFAULT_SLOT, help="booked minutes (default 90)")
    parser.add_argument("--split", default="20/60/20", help="PLAN/BUILD/REFLECT weights summing to 100")
    parser.add_argument("--plan-min", type=int, default=None)
    parser.add_argument("--build-min", type=int, default=None)
    parser.add_argument("--reflect-min", type=int, default=None)
    parser.add_argument("--opening", type=int, default=5)
    parser.add_argument("--closing", type=int, default=5)
    parser.add_argument("--rotation", type=int, default=10, help="minutes per driver in BUILD")
    parser.add_argument("--start", default=None, help="HH:MM in the local timezone (default: now)")
    parser.add_argument("--drivers", default=None, help='comma-separated driver order, e.g. "Ana,Joao"')
    parser.add_argument("--format", choices=("md", "json"), default="md")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    args = _build_parser().parse_args(argv)
    explicit = {name: value for name, value in (
        ("PLAN", args.plan_min), ("BUILD", args.build_min), ("REFLECT", args.reflect_min),
    ) if value is not None}
    try:
        drivers = _parse_drivers(args.drivers)
        schedule = build_schedule(
            duration=args.duration, slot=args.slot, split=_parse_split(args.split),
            phase_minutes=explicit, opening=args.opening, closing=args.closing,
            rotation=args.rotation, start=_parse_start(args.start, datetime.now().astimezone()),
        )
    except ScheduleError as err:
        print(f"mob_schedule: error: {err}", file=sys.stderr)
        return EXIT_INVALID
    if args.format == "json":
        print(json.dumps(schedule_to_dict(schedule, drivers), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(schedule, drivers), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

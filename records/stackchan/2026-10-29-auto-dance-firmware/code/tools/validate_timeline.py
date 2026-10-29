#!/usr/bin/env python3
"""Validate the compiled dance cue table without Arduino hardware."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKETCH = ROOT / "stackchan_dance" / "stackchan_dance.ino"

MAX_YAW = 480
MIN_PITCH = 180
MAX_PITCH = 720
MAX_SPEED = 900
ROUTINE_MS = 16000

CUE_RE = re.compile(
    r"\{\s*(?P<at>\d+)\s*,\s*(?P<yaw>[^,]+),\s*(?P<pitch>[^,]+),"
    r"\s*(?P<speed>[^,]+),\s*Expression::(?P<expression>\w+)\s*\}"
)


def resolve(value: str, constants: dict[str, int]) -> int:
    value = value.strip()
    if value.lstrip("-").isdigit():
        return int(value)
    if value not in constants:
        raise ValueError(f"unknown cue value: {value}")
    return constants[value]


def main() -> int:
    source = SKETCH.read_text(encoding="utf-8")
    constants = {
        name: int(value)
        for name, value in re.findall(
            r"constexpr int\s+(k(?:Yaw|Pitch|Max)\w*)\s*=\s*(-?\d+)\s*;", source
        )
    }
    constants.update({"kMaxServoSpeed": MAX_SPEED})

    matches = list(CUE_RE.finditer(source))
    if not matches:
        print("ERROR: no dance cues found", file=sys.stderr)
        return 1

    previous_at = -1
    expressions: set[str] = set()
    for index, match in enumerate(matches, start=1):
        at = int(match.group("at"))
        yaw = resolve(match.group("yaw"), constants)
        pitch = resolve(match.group("pitch"), constants)
        speed = resolve(match.group("speed"), constants)
        expression = match.group("expression")
        expressions.add(expression)

        if at <= previous_at:
            raise ValueError(f"cue {index}: timestamps are not strictly increasing")
        if at >= ROUTINE_MS:
            raise ValueError(f"cue {index}: {at} ms is outside the routine")
        if not -MAX_YAW <= yaw <= MAX_YAW:
            raise ValueError(f"cue {index}: yaw {yaw} exceeds the safety envelope")
        if not MIN_PITCH <= pitch <= MAX_PITCH:
            raise ValueError(f"cue {index}: pitch {pitch} exceeds the safety envelope")
        if not 0 <= speed <= MAX_SPEED:
            raise ValueError(f"cue {index}: speed {speed} exceeds the servo limit")
        previous_at = at

    required_expressions = {"Happy", "Excited", "Wink", "Love", "Cool", "Finale"}
    missing = required_expressions - expressions
    if missing:
        raise ValueError(f"missing expressions: {', '.join(sorted(missing))}")

    print(
        f"PASS: {len(matches)} cues, {len(expressions)} expressions, "
        f"{ROUTINE_MS / 1000:.1f}s loop, servo envelope yaw +/-{MAX_YAW / 10:.1f} deg "
        f"pitch {MIN_PITCH / 10:.1f}..{MAX_PITCH / 10:.1f} deg"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)

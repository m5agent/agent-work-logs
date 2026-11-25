#!/usr/bin/env python3
"""Decode the original Cardputer-ADV NEC demo's captured LEDC envelope."""

import argparse
import json
from pathlib import Path


CAPACITY = 192
FRAME_EDGES = 68
UNIT_US = 560  # IRremote's NEC_UNIT for the pinned example.


def _within(duration_ns, units):
    expected = units * UNIT_US * 1_000
    return expected * 3 <= duration_ns * 4 <= expected * 5


def _validate(capture):
    if not isinstance(capture, dict) or (
        capture.get("schema_version"), capture.get("gpio"), capture.get("time_base")
    ) != (1, 44, "qemu-virtual-ns"):
        raise ValueError("unexpected LEDC GPIO44 capture identity")
    first = capture.get("first_edge")
    next_edge = capture.get("next_edge")
    epoch = capture.get("gpio_epoch")
    edges = capture.get("edges")
    if (
        type(first) is not int or type(next_edge) is not int or first < 0
        or type(epoch) is not int or epoch < 0
        or not isinstance(edges, list) or len(edges) > CAPACITY
        or next_edge - first != len(edges)
    ):
        raise ValueError("unexpected LEDC edge window")
    previous = -1
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("invalid LEDC edge")
        at, hz, duty, period = (
            edge.get(field) for field in ("at_ns", "carrier_hz", "duty_count", "period_count")
        )
        if any(type(value) is not int or value < 0 for value in (at, hz, duty, period)) or at < previous:
            raise ValueError("invalid LEDC edge time or carrier")
        if (hz and not 0 < duty < period) or (not hz and (duty or period)):
            raise ValueError("invalid LEDC duty state")
        previous = at
    return first, edges


def _decode_frame(edges):
    for mark, space in zip(edges[::2], edges[1::2]):
        if not (37_000 <= mark["carrier_hz"] <= 39_000 and mark["duty_count"] == 76
                and mark["period_count"] == 256 and space["carrier_hz"] == 0):
            return None
    time = [edge["at_ns"] for edge in edges]
    if not (_within(time[1] - time[0], 16) and _within(time[2] - time[1], 8)):
        return None
    bits = 0
    for bit in range(32):
        i = 2 + 2 * bit
        if not _within(time[i + 1] - time[i], 1):
            return None
        duration = time[i + 2] - time[i + 1]
        if _within(duration, 3):
            bits |= 1 << bit
        elif not _within(duration, 1):
            return None
    command = (bits >> 16) & 0xff
    if not _within(time[-1] - time[-2], 1) or (bits >> 24) != (command ^ 0xff):
        return None
    return bits & 0xffff, command


def decode_capture(capture):
    """Return complete NEC frames retained in the bounded controller readback."""
    first, edges = _validate(capture)
    frames = []
    index = 0
    while index + FRAME_EDGES <= len(edges):
        value = _decode_frame(edges[index:index + FRAME_EDGES])
        if value is None:
            index += 1
            continue
        address, command = value
        frames.append({"first_edge": first + index, "address": address, "command": command})
        index += FRAME_EDGES
    return frames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--address", type=lambda value: int(value, 0), default=0x1111)
    parser.add_argument("--commands", type=lambda value: int(value, 0), nargs="+", required=True)
    args = parser.parse_args()
    frames = decode_capture(json.loads(args.capture.read_text()))
    observed = [(frame["address"], frame["command"]) for frame in frames]
    expected = [(args.address, command) for command in args.commands]
    count = len(expected)
    if not any(observed[index:index + count] == expected for index in range(len(frames) - count + 1)):
        raise SystemExit(f"NEC frames {observed!r} did not contain {expected!r}")
    print(json.dumps(frames))


if __name__ == "__main__":
    main()

# R2-CLA — closed-loop INPUT direction audit + fill (final summary)

- Generated: 2026-11-05T17:44:03+08:00
- Queue: 112 Unit-runtime-implemented Units with declared inputs; verdicts {"COVERED": 107, "PARTIAL": 5}
- Fresh round-2 executions on 8907 (new visible sessions, latest firmware): 16 Units (8 round-2-fresh lanes + wave re-runs)
- Candidates/mismatches: **none** (no zero-response, null, wrong-scaling or BLOCKED input case was found).

Read `coverage.md` for the full 112-row table, field-level evidence and the round-2
fresh-execution table; `results.json` is the machine-readable version;
`NOT-RUN.md` lists prior-only Units and host-port categories with explicit reasons.

## FAIL / PARTIAL list

- `cardkb2` PARTIAL 1/2 fields; missing: mode — CL-A wave1 latest-firmware (8907)
- `8servos2-i2c` PARTIAL 6/13 fields; missing: adc-values-hex, input-levels-hex, sys-dc-mv, sys-grove-mv, sys-ma, sys-ref-mv, timer-freq-hex — CL-A wave1 latest-firmware (8907)
- `step16` PARTIAL 4/7 fields; missing: led-config, rgb-brightness, rgb-power — CL-A wave1 latest-firmware (8907)
- `timerpwr` PARTIAL 3/13 fields; missing: backlight, battery-i-ma, cycle, grove-i, grove-output, grove-v, schedule-off, schedule-on, trigger-bits, usb-i — CL-A wave1 latest-firmware (8907)
- `mq` PARTIAL 8/9 fields; missing: ntc-mv — CL-A wave1 latest-firmware (8907)

## NOT RUN

- No Unit-runtime input Unit is NOT RUN; all 112 are covered/partial with evidence.
- Host-port-only categories (key/limit/pir/light/color/tof/ultrasonic-i2c/tvoc/env-iii as Units) are
  outside the Unit-runtime input lane; see NOT-RUN.md for the explicit mapping and owning lane.

All results are virtual-device validation on the canonical Unit runtime; no physical hardware claims.

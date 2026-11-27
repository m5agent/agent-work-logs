# LX6-B classic Stick board ports

- Date `2026-11-27`
- Result `PARTIAL` virtual-device validation
- Work type `code_change`
- Source esp32sim `m5/batch-lx6b` at `f528744221077c59a7ba6a5eeb146ec7bda90ff5`
- Environment native ESP32 simulator, mask ROM boot, catalog firmware and pinned Arduino-ESP32 builds

## Result

The six classic Stick profiles use the virtual ESP32 controllers and the shared LX6-C power models. Plus SE and Plus2 passed their runnable matrices and catalog boot/input checks. The batch ran 85 Arduino cases, with 83 passing and 2 failing. Seven additional cases have compile defects in the pinned documentation or its library API. The original M5Stick and StickT2 factory runs remain incomplete. Both exact-board controller probes passed.

## Evidence

- The four stock UIFlow2 home screens and UART0 A/B input checks passed.
- StickT2's separate controller probe validated two complete RAW14 frames and both encoder directions. M5Stick's probe read the IMU, magnetometer and shared IP5306, then verified native OLED pixels.
- Each case records the firmware SHA-256, runtime source and available stimulus or UART digests. [Case evidence](evidence/matrix-summary.json)
- The source branch was pushed to the fork. [Branch commit](https://github.com/m5agent/esp32sim/commit/f528744221077c59a7ba6a5eeb146ec7bda90ff5)

## Files

- [Report and per-case matrix](report.md)
- [Structured run](run.json)
- [Firmware, runtime and case evidence](evidence/matrix-summary.json)
- [NEC receive and raw PDM evidence](evidence/receiver-summary.json)

## Limits

Physical hardware validation was NOT RUN. The original factory firmware cases remain FAIL. The report records the Arduino library failures, baseline workspace exceptions and unsupported device behavior.

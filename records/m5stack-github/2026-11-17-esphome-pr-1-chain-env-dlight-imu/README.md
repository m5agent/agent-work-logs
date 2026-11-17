# m5stack/esphome #1: Chain ENV / DLight / IMU components

- Date: `2026-11-17`
- Result: `PARTIAL` (host-level build and host-level runtime test passed; no virtual device and no physical Chain hardware)
- Work type: `pr_review`
- Source: https://github.com/m5stack/esphome/pull/1 (opened 2026-11-17T03:45Z by New-Kringster, open, no prior comments)
- Source version: PR head `a5263dbfc71d1e33fa18d1690faa13c5adf89837` on base `feat-m5-chain` (`170093f52939d0496b05e52cf31009f8d67a5202`), 24 new files, 2171 lines
- Environment: macOS arm64, Python 3.13.15, ESPHome 2026.11.0-dev from the PR checkout; ESP-IDF 5.5.6 build; ESPHome **host** target plus a pseudo-terminal Chain simulator; no M5Stack Chain hardware, no virtual-device profile
- Evidence class: **host-level test** (build + runtime against a simulated Chain bus) plus **code-level verification** (protocol cross-check against `m5stack/M5Chain@277dcfe8`)

## Conclusion

The three components are wire-compatible with M5Stack's own Chain library: every
command code, payload order, unit and event bit layout matches
`m5stack/M5Chain` (ENV, DLight, IMU), and a host build with all three nodes on
one UART parses synthetic readings and `0xE0` reports into the expected sensor
and binary-sensor states. Two things should be fixed before merge:

1. **Alarms get no initial state when the matching reading is not configured.**
   `poll_next_()` only queues a read when a sensor entity exists, and the initial
   alarm state is published only from that read. An alarm-only configuration
   therefore issues **no read at all** and the binary sensor stays `unknown`
   until the device happens to cross a threshold (reproduced: 7 configuration
   frames, 0 reads, 0 states).
2. **No component test YAMLs.** All 14 existing Chain components ship
   `tests/components/<name>/`, so this PR's 2171 lines are never compiled by CI.
   `script/build_codeowners.py --check` also fails, which is a required CI step
   (`ci.yml:238`).

## Key evidence

- Build: `esphome compile` on `esp32dev`/ESP-IDF 5.5.6 succeeds; config valid.
- Runtime: host target + pty Chain simulator; the six boot settings of each node
  carry the expected payloads, readings decode to the synthetic values
  (23.50 °C / 45 % / 1013.2 hPa / 12.34 m / 1234 lx / 9.80665 m/s² / 27.50 °C),
  and the ENV/IMU/DLight event reports drive the mapped alarms on and off.
- Protocol: command/payload/mask table against `m5stack/M5Chain`.
- Gaps: `evidence/host-runtime.txt`, `evidence/alarm-only.txt`,
  `evidence/codeowners-check.txt`.

## Files

- `report.md`: full review, method, findings and limits
- `run.json`: structured record
- `evidence/`: build output, protocol cross-check, generated code, runtime logs
- `code/`: pty Chain simulator and the two host YAMLs (reproducible)

## Not covered

- `NOT RUN` virtual-device validation: the local Device Service exposes 36
  profiles and none is a Chain controller, and there is no Chain ENV/DLight/IMU
  peripheral model, so the real firmware/UART path cannot be exercised.
- `NOT RUN` hardware validation: no Chain Captain, Chain ENV, DLight or IMU on
  the bench during this review.
- `NOT RUN` DLight interrupt-mode interaction: whether lux keeps updating while
  the Dark/Bright alarm interrupts are enabled (the vendor library documents
  acquisition only outside the threshold band; unconfirmed either way here).

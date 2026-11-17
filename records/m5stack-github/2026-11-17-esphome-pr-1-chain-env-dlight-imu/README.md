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
2. **No component tests.** All 12 existing Chain components ship
   `tests/components/<name>/` (`common.yaml`, `test.esp32-idf.yaml` and a
   `<name>_test.cpp` unit test), so this PR's 2171 lines are never compiled or
   tested by CI.
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

## Follow-up: fix re-check at `419362b`

The author pushed `419362b4a274319d87d17d91941264f5ad26ac6f` ("Read the device
for an alarm that has no sensor of its own") and answered the three findings in
a PR comment. Re-checked on the host harness at that commit:

- **Alarm without a sensor — fixed.** A config with one alarm per node and no
  sensor entities (ENV temperature alarm on the AHT20 source, DLight
  `low_light`, IMU `motion`) now issues exactly one read per node and publishes
  each alarm's first state; the previous head issued zero reads and zero states.
  An all-alarm config without events (ENV temperature alarm on the SPA06 source
  plus humidity/pressure/altitude, DLight Dark+Bright, IMU motion/rotation/
  temperature) publishes all nine initial states from one read each and then
  stops polling. Injected `0xE0` reports still switch the alarms afterwards.
  Evidence: `evidence/round2-alarm-only.txt`,
  `evidence/round2-all-alarms-noevents.txt`.
- **Duplicate `set_update_interval` — fixed.** The generated `main.cpp` has one
  call per node, and an explicit `update_interval: 1s` still overrides the
  default. Evidence: `evidence/round2-codegen.txt`.
- **CODEOWNERS — pre-existing, confirmed.** `script/build_codeowners.py --check`
  fails on the base `170093f` without the PR and regeneration adds 66 lines;
  with this PR it adds 72 (each of the three components contributes two lines:
  the component and its `output` platform). The author's "69" matches the
  component count, not the CODEOWNERS line count. Evidence:
  `evidence/round2-codeowners.txt`.
- **Tests — not verifiable from the PR.** The three alarm-only unit tests the
  author mentions are not in the PR diff or on the fork branch, so they were
  `NOT RUN` here. CI on `419362b` is `action_required` (not executed), so the
  PR still has no automated compile/unit-test evidence for these components.
- **DLight in-band readings — author's hardware result.** The reported
  588 → 333 lx and 594 → 378 → 558 → 151 lx sequences at thresholds 10/2000 and
  10/800 answer the original question; this harness cannot reproduce the
  interrupt-mode interaction, so the hardware run is the only evidence.

`PARTIAL` limits are unchanged: no virtual Chain controller profile, no physical
Chain hardware on this side, and the author's unit tests and DLight hardware run
were not independently reproduced.

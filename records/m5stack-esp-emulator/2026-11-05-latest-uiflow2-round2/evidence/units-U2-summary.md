# U2 — remaining Unit batches on Device Service 8903 (round 2)

- Generated: 2026-11-05T17:44:14+08:00
- Lane: virtual-device validation (visible Device Service sessions; NOT physical hardware).
- Service: `<agent-service>` (token-less, canonical Unit runtime).
- Device/firmware: `cores3` `v2.5.5` sha256 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded` (latest UIFlow2 firmware from the campaign manifest).
- Runtime: `.work/goals/2026-11-04-uiflow-full/runtime-build/build-xtensa/qemu-system-xtensa` sha256 `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`.
- Coverage: **23 cases** = batch12b (7) + batch12c (4) + io (12).
- Result: **PASS 21**, PASS after rerun 0, FAIL reproduced 2, BLOCKED 0, NOT RUN 0.
- The 2 FAILs are both `known-blocker` (already-documented host/fixture gaps: UNIT-HOST-17 frozen Buzzer SoftTimer callback arity; S3 ADC calibration eFuse fixture for Angle read_uv). Each was rerun serially twice (rounds 2-3, concurrency 1, host load recorded): identical failure both times -> not load-induced. Buzzer with the documented `--buzzer-callback-arity-patch` diagnostic PASSes.
- A third serial pass (round 3) happened to re-run every case (superset of the two retries); all 21 non-failing cases passed again serially, confirming the round-1 results under lower host load.

## Coverage table

| batch | case | r1 | serial retries | final | checks | session_id | firmware base SHA | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| batch12b | bmm350 | PASS | PASS (rounds 3) | PASS | 15/15 | `83d21d6dfed94086b7106d2b87e5efa5` | yes |  |
| batch12b | ina226-10a | PASS | PASS (rounds 3) | PASS | 19/19 | `84c4e07a0b2042e99cfeab78b3c91a32` | yes |  |
| batch12b | ina226-1a | PASS | PASS (rounds 3) | PASS | 19/19 | `fd2c51c017e2412baea4abe00f37676c` | yes |  |
| batch12b | roller485 | PASS | PASS (rounds 3) | PASS | 26/26 | `79c1cdf8a738470d95dbd008fd74274d` | yes |  |
| batch12b | roller485-lite | PASS | PASS (rounds 3) | PASS | 26/26 | `3cd6fce95d4b46e2b78dccb6690a6644` | yes |  |
| batch12b | rollercan | PASS | PASS (rounds 3) | PASS | 26/26 | `d12fdf029eca4284b444bab4a34fe140` | yes |  |
| batch12b | rollercan-lite | PASS | PASS (rounds 3) | PASS | 26/26 | `17d7cae4b9094f9e99f822fe4306adc2` | yes |  |
| batch12c | 8servos2-chain | PASS | PASS (rounds 3) | PASS | 13/13 | `dcda7ca90f2b407c9f18bd81ed85ab4f` | yes |  |
| batch12c | cat1-cn | PASS | PASS (rounds 3) | PASS | 13/13 | `b318f348728d41ca9486d9e4ae252810` | yes |  |
| batch12c | chainbus | PASS | PASS (rounds 3) | PASS | 11/11 | `01e2fe0b557242e289cb768a48757bb0` | yes |  |
| batch12c | mini-imu-pro | PASS | PASS (rounds 3) | PASS | 14/14 | `267e36a433af4413b52836e4155ea448` | yes |  |
| io | angle | FAIL | FAIL/FAIL (rounds 2, 3) | **FAIL** | 4/5 | `de902785ec314758ba188e27f554e527` | yes | ADC calibration fixture gap already documented for this lane: the official Angle driver get_voltage() -> machine.ADC.read_uv() raises OSError(95) ESP_ERR_NOT_SUPPORTED because adc_cali_create_scheme_curve_fitting needs S3 ADC calibration eFuse bits that this Device Service lane does not inject (docs/validation-ledger.md UNIT-01: read_uv/humidity need the S3 ADC calibration eFuse fixture, NOT RUN; docs/evidence/2026-11-02-unit-batch1/README.md:103; issue #9 synthetic ADC calibration eFuse is applied for Cardputer-ADV sessions, not here). Deterministic: identical OSError in two serial retries; not a timeout/frame or load artifact. |
| io | buzzer | FAIL | FAIL/FAIL (rounds 2, 3) | **FAIL** | 6/6 | `34ba9c74ae99401a8871ed71d7a7b1df` | yes | Frozen UIFlow2 Buzzer/Haptic driver gap, already documented as UNIT-HOST-17 (docs/unit-integration-host-issues.md): the frozen no-arg Haptic._cb is passed to SoftTimerScheduler.update, which calls callback(timer) -> TypeError -> background thread exits, so the natural one-shot duty->0 window is never observed (IO_BUZZER_TIMER_DONE appears via the probe's fallback). The repo provides an explicit opt-in generated-wrapper adapter (--buzzer-callback-arity-patch); this round's diagnostic with that adapter PASSes, confirming the root cause, while the unpatched frozen-driver case remains a documented OPEN host issue. Not load-induced: reproduced identically in two serial retries. |
| io | dual-button | PASS | PASS (rounds 3) | PASS | 8/8 | `182a6f5302c24bbd987a64aa7fc8a409` | yes |  |
| io | fan | PASS | PASS (rounds 3) | PASS | 8/8 | `1e91f26bbda54dd18e4966092179ed31` | yes |  |
| io | hub | PASS | PASS (rounds 3) | PASS | 9/9 | `896db3edad824a48b220473ef42ec9ee` | yes |  |
| io | ir | PASS | PASS (rounds 3) | PASS | 11/11 | `7d43c58c15b749f1971b59d28712a60f` | yes |  |
| io | key | PASS | PASS (rounds 3) | PASS | 8/8 | `2ade56c15cdc483db03fbed0000cf1cb` | yes |  |
| io | light | PASS | PASS (rounds 3) | PASS | 9/9 | `d38f10dd594b45398aedfd8a23290e0f` | yes |  |
| io | limit | PASS | PASS (rounds 3) | PASS | 8/8 | `6c2bff30c3ce4bdd97bcfadbcd8f603f` | yes |  |
| io | pir | PASS | PASS (rounds 3) | PASS | 8/8 | `2067fe4bf20e4c3aac386ed8706a4055` | yes |  |
| io | rgb | PASS | PASS (rounds 3) | PASS | 8/8 | `88783b4637e84920ac95be8bdfcf52ed` | yes |  |
| io | rs485 | PASS | PASS (rounds 3) | PASS | 9/9 | `14d3ca671f094167bc91c11bedfa4e7b` | yes |  |

## Failures reproduced in round 2 (candidates/)

- **io/angle** — `known-blocker`; ADC calibration fixture gap already documented for this lane: the official Angle driver get_voltage() -> machine.ADC.read_uv() raises OSError(95) ESP_ERR_NOT_SUPPORTED because adc_cali_create_scheme_curve_fitting needs S3 ADC calibration eFuse bits that this Device Service lane does not inject (docs/validation-ledger.md UNIT-01: read_uv/humidity need the S3 ADC calibration eFuse fixture, NOT RUN; docs/evidence/2026-11-02-unit-batch1/README.md:103; issue #9 synthetic ADC calibration eFuse is applied for Cardputer-ADV sessions, not here). Deterministic: identical OSError in two serial retries; not a timeout/frame or load artifact.
- **io/buzzer** — `known-blocker`; Frozen UIFlow2 Buzzer/Haptic driver gap, already documented as UNIT-HOST-17 (docs/unit-integration-host-issues.md): the frozen no-arg Haptic._cb is passed to SoftTimerScheduler.update, which calls callback(timer) -> TypeError -> background thread exits, so the natural one-shot duty->0 window is never observed (IO_BUZZER_TIMER_DONE appears via the probe's fallback). The repo provides an explicit opt-in generated-wrapper adapter (--buzzer-callback-arity-patch); this round's diagnostic with that adapter PASSes, confirming the root cause, while the unpatched frozen-driver case remains a documented OPEN host issue. Not load-induced: reproduced identically in two serial retries.

## BLOCKED

- none

## Diagnostics (explicit probe adaptations, not verdicts)

- **buzzer-callback-arity-patch** — status `PASS`; flavor `custom-guest-buzzer-callback-arity-patch`; evidence `.work/uiflow-latest-20261105/round2/units/U2/diagnostics/buzzer-patched/buzzer`. Explicit documented runner adaptation (patches/uiflow2-unit-buzzer): generated guest wrapper accepts SoftTimer's timer argument and calls the frozen no-arg callback. This is a diagnostic contrast for the unpatched frozen-driver failure; it does NOT replace the unpatched case verdict.

## NOT RUN

- none

## Method notes

- Each case is one visible Device Service session: runner builds the guest image from the latest cores3 base + probe tree, uploads it, creates the session with the Unit attachment/fixtures, waits for the probe marker, captures serial/QOM/frame evidence, requests the evidence ZIP before stopping, and stops with `purge=0` (history retained).
- PASS means the checked-in runner's own `result.json` status is PASS (all of its checks true); no assertion, fixture, check or timeout was modified. Round-2 status is the rerun result for round-1 failures only.
- Derived runners (batch12b/batch12c): only mechanical path edits (repo root, import path, probe tree, canonical runtime identity BINARY). See `derived-diffs/README.md` and the `.diff` files.
- Firmware identity: every case's `base_firmware_sha256` is compared to the manifest cores3 sha256; batch12b/batch12c also record the runtime binary sha256, which equals the canonical runtime `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`. `run_io_cases.py` records the session evidence manifest; the lane runtime is the service's canonical build.

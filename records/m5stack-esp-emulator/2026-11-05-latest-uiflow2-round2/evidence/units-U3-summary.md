# R2-U3: control + sensor batches and 9 runner-less Units closed-loop validation

- **Service**: token-less agent-owned Device Service `<agent-service>` (visible sessions, `/program` live program transport, evidence ZIP before stop, `purge=0`).
- **Canonical Unit-model runtime**: QEMU binary sha256 `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068` (`.work/goals/2026-11-04-uiflow-full/runtime-build/build-xtensa/qemu-system-xtensa`, per RUNBOOK2). `scroll` and `flashlight` probes independently passed their runtime-provenance pins against this sha; all other cases ran on the same service worker generation.
- **Firmware identity**: every executed case records the composed-image sha256 and its base image; **22/22 firmware-capable cases** resolve to the latest-firmware manifest sha256 (cores3 v2.5.5 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded`, sticks3 v2.5.5 `fd85648dfa1fd9656448aa45e86ee63be537a4534e959e422c0be4d45b3466c7`). Base identity sources: runner `base_firmware_sha256`, session `firmware_provenance.metadata.base_sha256`, or the host-measured runner-lane base file.
- **Validation lane**: `virtual-device validation`; hardware (`NOT RUN`). No tracked files modified; no gh/glab writes. At most 2 concurrent guests for batch runners, 1 concurrent guest for the closed-loop probes after the Lead host-load warning.
- **Coverage**: **24 Units / 24 cases** = control runner 5 + sensor runner 7 + service runner 3 + runner-less closed-loop 9. **PASS 22**, **BLOCKED 2**, **FAIL 0**.

## Control Unit batch (`tests/units/run_control_cases.py`, assertions unchanged)

| # | Unit | device | status | checks | session | evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | joystick-v11 | cores3 | **PASS** | 4/4 | `f8370f61fbd64617` | `.work/uiflow-latest-20261105/round2/units/U3/control-joystick-v11/joystick-v11` |
| 2 | encoder | cores3 | **PASS** | 5/5 | `b21f14a79065402c` | `.work/uiflow-latest-20261105/round2/units/U3/control-encoder/encoder` |
| 3 | 8encoder | cores3 | **PASS** | 6/6 | `19d52fc2d5b847c9` | `.work/uiflow-latest-20261105/round2/units/U3/control-8encoder/8encoder` |
| 4 | cardkb | cores3 | **PASS** | 7/7 | `13eed613f24f45ba` | `.work/uiflow-latest-20261105/round2/units/U3/control-cardkb/cardkb` |
| 5 | rfid2 | cores3 | **PASS** | 7/7 | `401d7681f5074bc7` | `.work/uiflow-latest-20261105/round2/units/U3/control-rfid2/rfid2` |

Closed-loop content per case (from the runner's own frozen assertions): official frozen driver ready, injected/probed I2C data reaches the guest, same-guest controller counters, output write→read back where applicable (encoder LED writes read back; cardkb keys/modifiers via I2C; joystick-v11 raw bytes; rfid2 card UID/data), evidence-before-stop and stopped-with-history.

## Sensor Unit batch (`tests/units/run_sensor_cases.py`, assertions unchanged)

| # | Unit | device | injected fixture waves | guest observed | status | checks | session |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | color | cores3 | clear-raw=42000, red-raw=9000, green-raw=6000, blue-raw=3000 -> guest_observed; clear-raw=53000, red-raw=21000, green-raw=12000, blue-raw=6000 -> guest_observed | yes | **PASS** | 15/15 | `c10a79fb0c9642ae` |
| 2 | tof | cores3 | distance-mm=321 -> guest_observed; distance-mm=1456 -> guest_observed | yes | **PASS** | 18/18 | `08cc71e4d4d547ad` |
| 3 | ncir | cores3 | ambient-c=17.3, object-c=37.1 -> guest_observed; ambient-c=31.5, object-c=53.2 -> guest_observed | yes | **PASS** | 14/14 | `4b94793090a6462b` |
| 4 | heart | cores3 | ir-sample=41000, red-sample=36000 -> guest_observed; ir-sample=12000, red-sample=9000 -> guest_observed | yes | **PASS** | 18/18 | `8cdc5fdf9f2e4fc6` |
| 5 | tvoc | cores3 | eco2-ppm=1250, tvoc-ppb=230, raw-h2=26000, raw-ethanol=31000 -> guest_observed; eco2-ppm=675, tvoc-ppb=18, raw-h2=18300, raw-ethanol=24500 -> guest_observed | yes | **PASS** | 19/19 | `777ffccf614b4187` |
| 6 | ultrasonic-i2c | cores3 | distance-mm=1234.5 -> guest_observed; distance-mm=876.2 -> guest_observed | yes | **PASS** | 14/14 | `f12fdc8f58174cf3` |
| 7 | thermal | cores3 | MLX90640 public-example reference fixture frame set (fixture sha256 a43a9db4edfc543b...; 768 finite pixels, 9 reference samples within 0.05C; live QOM source) | yes | **PASS** | 16/16 | `9f6f18aa392f40ef` |

Every sensor case includes the runner's negative-control matrix (identity/status/PEC/command-bit/saturation/overflow paths per the frozen fixture) plus `same_guest_input_1/2`, `live_controller_state`, `real_i2c_data_plane`, frame availability and evidence-before-stop checks.

## Service runner Units (`tests/units/run_service_cases.py`, closed-loop input/read + output/observe)

| # | Unit | direction | status | checks | session | evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | button | input: injected press -> guest GPIO read + QOM | **PASS** | 6/6 | `e0a8d64a7819422b` | `.work/uiflow-latest-20261105/round2/units/U3/service-all/button` |
| 2 | relay | output: guest GPIO write -> QOM readback | **PASS** | 6/6 | `d1180999df8c4282` | `.work/uiflow-latest-20261105/round2/units/U3/service-all/relay` |
| 3 | env-iii | input: injected T/RH/P -> official driver compensation read | **PASS** | 6/6 | `64f4e497091347ad` | `.work/uiflow-latest-20261105/round2/units/U3/service-all/env-iii` |

## The 9 runner-less Units: closed-loop matrix

| # | Unit | direction | injected / guest write | guest read (driver API) | host observation (QOM / controller) | waves | status | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2relay | output (GPIO) | guest `Relay2Unit.set_relay_cntrl(1,1)(2,0)` then after hard reset white/yellow write | `guest_transitions_reach_both_qom_channels` | `output-1-level/transitions`, `output-2-level/transitions` QOM: first `1/true,2/true`, reset `0/0` rebased, white->`1,0`, yellow->`1,1`; markers FIRST_BOTH_HIGH/SECOND_* | reset + 2 rebased waves | PASS | .work/uiflow-latest-20261105/round2/units/U3/relay2 |
| 2 | scroll | input + output (I2C) | host `/unit-input` 10 waves `source-count` / `pressed` (e.g. 0->115, 116, 117; rejected: -32768, 32768, mixed, overflow) | official `ScrollUnit.get_rotary_*` APIs across 22 `/program` executions | QOM `counter/increments/direction/ab-direction/led-rgb` matched expected rotation/AB phase and guest LED writes; 4 negative controls rejected with `invalid_unit_input` without state change | 22 exec / 10 injects | PASS | .work/uiflow-latest-20261105/round2/units/U3/scroll |
| 3 | flashlight | output (GPIO digital) | guest `FlashLightUnit.flash(BRIGHTNESS_100, TIME_220MS, False)` then `flash(0, TIME_220MS, True)` | constructor cold-low + flash/off API return | QOM `en-level false->true->false`, `active`, `pulse-count 0->1->0`, `last-program-count 1`, `flash-level-pct 100`, `timeout-ms 220`, `decoded-programs 1`, `output-known/pad-synchronized` true | 3 waves same guest | PASS | .work/uiflow-latest-20261105/round2/units/U3/flashlight/cores3 |
| 4 | servo8-hat | output (I2C, sticks3 HAT2-BUS) | guest `Servos8Hat.power_on(); write_servo_angle(1,90)` then `write_servo_angle(2,45); power_off()` | `read_servo_angle(1)=90`, `read_servo_angle(2)=45`, `get_power_state()` 1 then 0 | QOM `angles[0]=90`, `angles[1]=45`, `power-state 1->0`; output-transitions increment | 2 waves | PASS | .work/uiflow-latest-20261105/round2/units/U3/servo8hat |
| 5 | 8servos | output (I2C) | guest `Servos8Unit.set_mode(SERVO_CTL_MODE,0); set_servo_angle(90,0)` then `set_mode(...,1); set_servo_angle(30,1)` | `get_servo_angle(0)=90`, `get_mode(0)=3`; `get_servo_angle(1)=30`, `get_mode(1)=3` | QOM `modes=[3,0..]`, `angles=[90,0..]` then `modes=[3,3,0..]`, `angles=[90,30,0..]` | 2 waves | PASS | .work/uiflow-latest-20261105/round2/units/U3/8servos |
| 6 | joystick2 | input (I2C) | host initial + `/unit-input`: `(x=1000,y=-1000,button=false)` then `(x=-2048,y=2048,button=true)` | `Joystick2Unit.get_axis_position()`, `get_button_status()` -> `(1000,-1000)/0` then `(-2048,2048)/1` | QOM `x-position/y-position/button-pressed` equal injected values in both waves (`input-events` counted) | 2 waves | PASS | .work/uiflow-latest-20261105/round2/units/U3/joystick2 |
| 7 | nfc | input (I2C, controller-provided tag) | deterministic ST25R3916 fixture tag (controller state `tag-uid`), two detect waves | `NFCUnit.detect()` -> `card.uid_str = DEADBEEF`, `type_name` printed | controller QOM `tag-uid = DEADBEEF` equals guest UID in both waves; transactions/read/write byte counters advance (`548/148/470`) | 2 waves | PASS | .work/uiflow-latest-20261105/round2/units/U3/nfc |
| 8 | mini-bps-v11 | n/a | no model / no driver | not executable | not executable | - | BLOCKED | catalog entry (runtime=planned) |
| 9 | mini-pdm | n/a | no model / no driver | not executable | not executable | - | BLOCKED | catalog entry (runtime=planned) |

`scroll` and `2relay` reuse the checked-in Device Service probes (`tests/units/run_live_scroll.py`, `tests/units/run_relay_reset_probe.py`); `flashlight` reuses `tests/units/run_flashlight_route_probe.py`; the four new probes are in `round2/units/U3/tools/u3_live_probe.py` + `specs/*.json` (official frozen drivers from the firmware `unit`/`hat` packages; inputs injected via `/unit-input`, outputs observed from `/units` QOM).

## BLOCKED / NOT RUN (no PASS claimed)

### mini-bps-v11

- status: **BLOCKED** | classification: `known-blocker`
- reason: catalog runtime=planned (0143 DEFER 未实现): QMP6988 address unresolved 0x56 vs frozen driver 0x70; no QEMU model, host_admission=false on every device
- catalog: `platform/units/catalog.json` runtime=planned, host_admission=false on every device; see `candidates/mini_bps_v11_no_model.md`.

### mini-pdm

- status: **BLOCKED** | classification: `known-blocker`
- reason: catalog runtime=planned (0145 DEFER 未实现): public UIFlow2 has no Unit PDM driver (SPM1423 PDM is board-level I2S); Unit attachment cannot bind; host_admission=false
- catalog: `platform/units/catalog.json` runtime=planned, host_admission=false on every device; see `candidates/mini_pdm_no_model.md`.

No other Unit was NOT RUN: all 22 model-backed Units executed on the canonical Unit-model runtime. There were **no FAIL cases**, so no failure candidate cards were produced for U3.

## Evidence layout

```
.work/uiflow-latest-20261105/round2/units/U3/
  results.json                     # 24 cases, per-case firmware/base sha, checks, matrix data
  summary.md                       # this file
  candidates/*.md                  # 2 known-blocker cards (mini-bps-v11, mini-pdm)
  control-<case>/<case>/           # runner result.json, evidence.zip, frame.png, serial.txt, image
  sensor-<case>/<case>/            # same, plus injections[] guest_observed evidence
  service-all/<case>/              # button/relay/env-iii closed-loop runner results
  scroll/                          # run_live_scroll.py plan+execute report, 22 executions, 10 injections
  flashlight/cores3/               # run_flashlight_route_probe.py report
  relay2/                          # run_relay_reset_probe.py (2relay) report
  joystick2|nfc|8servos|servo8hat/ # new closed-loop probes: report.json, serial.txt, waves/injections, evidence.zip
  specs/                           # per-Unit closed-loop spec (waves, injected values, expected QOM/guest reads)
  tools/u3_live_probe.py           # generic live-program closed-loop driver
```

## Reproduce

```sh
# control / sensor / service batches (assertions unchanged)
PYTHONPATH=platform/tools:tests/uiflow2 .work/issue-review-venv/bin/python3.12 tests/units/run_control_cases.py \
  --api-url <agent-service> --case <joystick-v11|encoder|8encoder|cardkb|rfid2> --out-dir <dir>
PYTHONPATH=platform/tools:tests/uiflow2 .work/issue-review-venv/bin/python3.12 tests/units/run_sensor_cases.py \
  --api-url <agent-service> --case <color|tof|ncir|heart|tvoc|ultrasonic-i2c|thermal> --out-dir <dir>
PYTHONPATH=platform/tools:tests/uiflow2 .work/issue-review-venv/bin/python3.12 tests/units/run_service_cases.py \
  --api-url <agent-service> --case all --out-dir <dir>
# runner-less Unit closed-loop (example: joystick2 input injection)
.work/issue-review-venv/bin/python3.12 .work/uiflow-latest-20261105/round2/units/U3/tools/u3_live_probe.py \
  --api <agent-service> --device cores3 --unit-id joystick2 --port-id port-a \
  --spec-json .work/uiflow-latest-20261105/round2/units/U3/specs/joystick2.json --out-dir <dir>
```

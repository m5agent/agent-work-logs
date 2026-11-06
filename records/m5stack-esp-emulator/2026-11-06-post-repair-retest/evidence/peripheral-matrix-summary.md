# P1 sim-peripheral — full tracked peripheral matrix on repaired runtime (2026-11-06)

Scope: `.work/retest-20261106/peripheral-matrix/`. Tracked runner `tests/uiflow2/run_peripheral_matrix.py` (unmodified, source `dd2eb35d`), all 68 checked-in peripheral-matrix cases, **direct QEMU** on the repaired native runtime. Virtual-device validation — not physical hardware.

## Run identity

| field | value |
| --- | --- |
| source head | `dd2eb35d` |
| python | 3.13.15 (system 3.13 + `PYTHONPATH=.work/py:platform/tools:tests/uiflow2`) |
| command | `python3 tests/uiflow2/run_peripheral_matrix.py --out-dir .work/retest-20261106/peripheral-matrix` |
| M5_QEMU_XTENSA | `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e` (`.work/issue-repair-20261105/runtime-clean/...`, repaired) |
| M5_QEMU_RISCV32 | `25497c521ebd5838a56b066551dd5c33d6dd00df853ed4a256fcca79944de7db` (documented repaired C6 runtime) |
| ROM dirs | `<repo>/.work/M5StopWatch-QEMU/build/qemu/pc-bios`, `<repo>/.work/M5StopWatch-QEMU/build/qemu-c6/pc-bios` |
| firmware manifest | `.work/uiflow-latest-20261105/firmware/manifest.json` (refreshed latest official images) |
| concurrency / host load | 1 QEMU at a time (max 2 allowed); recorded load samples: 9.06 5.79 4.07 → 8.79 9.72 7.57 (other round-3 scopes active; cannot reduce below 1) |

## Result

| metric | value |
| --- | --- |
| case ids executed | **68 / 68** |
| main observation: FAIL | 2 |
| main observation: PASS | 66 |
| FAILs re-run once (same command/runtime/firmware) | 2 |
| transient / load-induced (recovered or classified INFRA-LOAD) | core2-axp192, stackchan-peripherals |

Repair verification against closed issues #172–#187 (P1 relevant subset):

| issue | scope | covered by this run | result | detail |
| --- | --- | --- | --- | --- |
| **#175** | ED2208 partial window + AUTO refresh | papercolor-peripherals, papercolor-sd, papercolor-audio, papercolor-sht4x, papercolor-mic, papercolor-ir, papercolor-rgb | **PASS** | All PaperColor cases (frame markers + peripherals serial + SD/PCM/RGB oracles) must pass on the repaired ED2208 model. |
| **#176** | AXP2101 charger semantics | cores3-power-transitions, core2-axp192 | **PASS** | cores3-power-transitions requires 87 4000 1 -> 64 3600 0 -> 93 4200 1 and DONE PASS; core2-axp192 (AXP192, separate model) also rerun. |
| **#177** | SHA-bound official driver expectations | sticks3-peripherals, papercolor-peripherals | **PASS** | Only StickS3 BMI270 axis and PaperColor undetermined-charge cases bind replacements to the exact base firmware sha; each must pass with the replacement marker observed in serial. |
| **#185** | Executed runtime provenance | sticks3-peripherals, sticks3-audio, sticks3-mic, cardputer-adv-sd, cores3-sd, cardputer-adv-imu, cardputer-adv-keyboard … | **PASS** | Every case command must reference the repaired runtime path and every base firmware sha must match the refreshed manifest; runtime sha256 27df1b40.. (xtensa) / 25497c52.. (riscv32) recorded. |
| **#186** | CoreS3 ADC calibration admission (Angle/Light units) | — | **NOT COVERED BY P1** | The 68-case peripheral matrix has no Angle/Light or generic ADC Unit case; #186 is covered by the round-3 Unit battery (U1) — cross-reference, not a P1 gap. |

Cross-reference: #172/#173/#174/#179/#183/#184/#187 are device-matrix/boot items outside P1; #178 classic Flash transport; #180/#181/#182/#187 boot/UART0 observation; #188 Tab5 remains open. **#186 (CoreS3 ADC calibration / Angle-Light) is NOT COVERED by P1** (no Angle/Light/ADC Unit case in the 68-case matrix; it is covered by the round-3 Unit battery U1).

Merged-fix note: **core2-mic PASS** in this fresh run — the pre-merge repair matrix preserved a Core2 Mic frame failure; merged commit 7c696e3c ("test: wait for Core2 microphone draw completion") is in git log between the repair-phase tree eba761b and HEAD dd2eb35d.

## 68-case table

| # | case | device | firmware | status | rerun (2nd observation) | validation | repair verification | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | sticks3-peripherals | m5sticks3 | v2.5.5 `fd85648dfa` | **PASS** | — | PASS serial markers: STICKS3_PM1_BUTTON_CFG, STICKS3_IMU_TYPE 6, STICKS3_BATTERY 87 4000 0, STICKS3_BTN_A 1, STICKS3_BTN_B 1, STICKS3_BTN_PWR 1, STICK | #177 | `.work/retest-20261106/peripheral-matrix/sticks3-peripherals` |
| 2 | sticks3-audio | m5sticks3 | v2.5.5 `fd85648dfa` | **PASS** | — | PCM bytes=126976 samples=63488 nonzero=44088 peak_to_peak=2881 \| PASS StickS3 audio marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/sticks3-audio` |
| 3 | sticks3-mic | m5sticks3 | v2.5.5 `fd85648dfa` | **PASS** | — | PASS StickS3 mic marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/sticks3-mic` |
| 4 | cardputer-adv-sd | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | disk image=.work/retest-20261106/peripheral-matrix/cardputer-adv-sd/sd.img sector=100 length=512 match=True \| PASS Cardputer-ADV SD marker rgb=(0,255 | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-sd` |
| 5 | cores3-sd | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — | PASS serial markers: CORES3_SD_RW_PASS, CORES3_SD_DRAW_COMPLETE \| disk image=.work/retest-20261106/peripheral-matrix/cores3-sd/sd.img sector=100 leng | #185 provenance | `.work/retest-20261106/peripheral-matrix/cores3-sd` |
| 6 | cardputer-adv-imu | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | PASS Cardputer-ADV BMI270 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-imu` |
| 7 | cardputer-adv-keyboard | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | PASS Cardputer-ADV TCA8418 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-keyboard` |
| 8 | cardputer-adv-nfc | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | PASS Cardputer-ADV NFC marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-nfc` |
| 9 | cardputer-adv-cc1101 | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | PASS Cardputer-ADV CC1101 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-cc1101` |
| 10 | cardputer-adv-audio | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | PCM bytes=182272 samples=91136 nonzero=47920 peak_to_peak=46091 \| PASS Cardputer-ADV audio marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-audio` |
| 11 | cardputer-adv-mic | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | PASS Cardputer-ADV mic marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-mic` |
| 12 | atoms3r-peripherals | m5atoms3r | v2.5.4 `c289f7df74` | **PASS** | — | PASS serial markers: ATOMS3R_IMU_TYPE 6, ATOMS3R_BTN 1, ATOMS3R_ACCEL -0.50 -0.25 0.75, ATOMS3R_GYRO -20.02 -10.01 30.03, ATOMS3R_MAG -29.99 -19.49 -8 | #185 provenance | `.work/retest-20261106/peripheral-matrix/atoms3r-peripherals` |
| 13 | sticks3-ir | m5sticks3 | v2.5.5 `fd85648dfa` | **PASS** | — | PASS NEC offset=0 address=0x56 command=0xa3 | #185 provenance | `.work/retest-20261106/peripheral-matrix/sticks3-ir` |
| 14 | sticks3-ir-rx | m5sticks3 | v2.5.5 `fd85648dfa` | **PASS** | — | PASS IR RX marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/sticks3-ir-rx` |
| 15 | cores3-peripherals | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — | PASS serial markers: CORES3_IMU_TYPE 6, CORES3_POWER 87 4000 1, CORES3_ALS 640 321, CORES3_MAG, CORES3_TOUCH, CORES3_BTN_PWR 1, CORES3_IMU 0.250 -0.50 | #185 provenance | `.work/retest-20261106/peripheral-matrix/cores3-peripherals` |
| 16 | cores3-power-transitions | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — | PASS serial markers: CORES3_POWER_TRANS 87 4000 1, CORES3_POWER_TRANS 64 3600 0, CORES3_POWER_TRANS 93 4200 1, CORES3_POWER_TRANS_DONE PASS \| PASS Co | #176 | `.work/retest-20261106/peripheral-matrix/cores3-power-transitions` |
| 17 | cores3-usb-hid | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — |  | #185 provenance | `.work/retest-20261106/peripheral-matrix/cores3-usb-hid` |
| 18 | cores3-camera | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — | PASS serial markers: CORES3_CAMERA_PASS 320x240 153600 bytes, CORES3_CAMERA_FRAMESTREAM PASS 1 | #185 provenance | `.work/retest-20261106/peripheral-matrix/cores3-camera` |
| 19 | stackchan-camera | m5stackchan | v2.5.5 `d87f2d50dd` | **PASS** | — | PASS serial markers: CORES3_CAMERA_PASS 320x240 153600 bytes | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-camera` |
| 20 | cores3-audio | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — | PCM bytes=41984 samples=20992 nonzero=20957 peak_to_peak=11523 \| PASS CoreS3 audio marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cores3-audio` |
| 21 | cores3-mic | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — | PASS CoreS3 mic marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cores3-mic` |
| 22 | stamplc-peripherals | m5stamplc | v2.5.4 `cade08fdfb` | **PASS** | — | PASS serial markers: STAMPLC_PERIPHERAL_MAIN, STAMPLC_RELAY 1 PRESS 1, STAMPLC_INPUTS, STAMPLC_INA 12.00 0.500, STAMPLC_INA 15.00 0.750, STAMPLC_RGB T | #185 provenance | `.work/retest-20261106/peripheral-matrix/stamplc-peripherals` |
| 23 | stopwatch-peripherals | m5stopwatch | v2.5.5 `0bcb9269f4` | **PASS** | — | PASS serial markers: STOPWATCH_PM1_BUTTON_CFG, STOPWATCH_IMU_TYPE 6, STOPWATCH_POWER 87 4000 1, STOPWATCH_RTC 2026-10-22 07:08:09, STOPWATCH_TOUCH, ST | #185 provenance | `.work/retest-20261106/peripheral-matrix/stopwatch-peripherals` |
| 24 | papermono-peripherals | m5papermono | v2.5.4 `f30eda56dc` | **PASS** | — | PASS serial markers: PAPERMONO_PM1_BUTTON_CFG, PAPERMONO_IMU_TYPE 6, PAPERMONO_POWER 87 4000 1, PAPERMONO_RTC 2026-10-22 07:08:09, PAPERMONO_SD rw ok, | #185 provenance | `.work/retest-20261106/peripheral-matrix/papermono-peripherals` |
| 25 | papermono-buzzer | m5papermono | v2.5.4 `f30eda56dc` | **PASS** | — | PASS serial markers: PAPERMONO_BUZZER ok 3500Hz \| PCM bytes=161792 samples=80896 nonzero=43349 peak_to_peak=65535 \| PASS PaperMono buzzer marker rgb | #185 provenance | `.work/retest-20261106/peripheral-matrix/papermono-buzzer` |
| 26 | papermono-pdm-mic | m5papermono | v2.5.4 `f30eda56dc` | **PASS** | — | PASS PaperMono PDM mic marker rgb=(0,0,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/papermono-pdm-mic` |
| 27 | papermono-rgb | m5papermono | v2.5.4 `f30eda56dc` | **PASS** | — | PASS PaperMono RGB marker rgb=(0,0,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/papermono-rgb` |
| 28 | papercolor-peripherals | m5papercolor | v2.5.4 `ccffe79f97` | **PASS** | — | PASS serial markers: PAPERCOLOR_PM1_BUTTON_CFG, PAPERCOLOR_PERIPHERAL_MAIN, PAPERCOLOR_POWER 87 4000 0, PAPERCOLOR_POWER_STATE 3400 0, PAPERCOLOR_POWE | #175 + #177 | `.work/retest-20261106/peripheral-matrix/papercolor-peripherals` |
| 29 | papercolor-sd | m5papercolor | v2.5.4 `ccffe79f97` | **PASS** | — | disk image=.work/retest-20261106/peripheral-matrix/papercolor-sd/sd.img sector=100 length=512 match=True \| PASS PaperColor SD marker rgb=(0,0,0) | #175 | `.work/retest-20261106/peripheral-matrix/papercolor-sd` |
| 30 | papercolor-audio | m5papercolor | v2.5.4 `ccffe79f97` | **PASS** | — | PCM bytes=485376 samples=242688 nonzero=88180 peak_to_peak=2881 \| PASS PaperColor audio marker rgb=(0,0,0) | #175 | `.work/retest-20261106/peripheral-matrix/papercolor-audio` |
| 31 | papercolor-sht4x | m5papercolor | v2.5.4 `ccffe79f97` | **PASS** | — | PASS PaperColor SHT4X marker rgb=(0,0,0) | #175 | `.work/retest-20261106/peripheral-matrix/papercolor-sht4x` |
| 32 | papercolor-mic | m5papercolor | v2.5.4 `ccffe79f97` | **PASS** | — | PASS PaperColor mic marker rgb=(0,0,0) | #175 | `.work/retest-20261106/peripheral-matrix/papercolor-mic` |
| 33 | papermono-nfc | m5papermono | v2.5.4 `f30eda56dc` | **PASS** | — | PASS NFC marker rgb=(0,0,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/papermono-nfc` |
| 34 | papermono-lora | m5papermono | v2.5.4 `f30eda56dc` | **PASS** | — | PASS LoRa marker rgb=(0,0,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/papermono-lora` |
| 35 | stackchan-nfc | m5stackchan | v2.5.5 `d87f2d50dd` | **PASS** | — | PASS NFC marker rgb=(0,0,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-nfc` |
| 36 | stackchan-touch | m5stackchan | v2.5.5 `d87f2d50dd` | **PASS** | — | PASS Si12T touch marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-touch` |
| 37 | stackchan-rgb | m5stackchan | v2.5.5 `d87f2d50dd` | **PASS** | — | PASS StackChan RGB marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-rgb` |
| 38 | stackchan-audio | m5stackchan | v2.5.5 `d87f2d50dd` | **PASS** | — | PCM bytes=41984 samples=20992 nonzero=20957 peak_to_peak=11523 \| PASS StackChan audio marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-audio` |
| 39 | stackchan-mic | m5stackchan | v2.5.5 `d87f2d50dd` | **PASS** | — | PASS StackChan mic marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-mic` |
| 40 | stackchan-peripherals | m5stackchan | v2.5.5 `d87f2d50dd` | **FAIL** | FAIL (attempt 1) |  | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-peripherals` |
| 41 | stackchan-servo | m5stackchan | v2.5.5 `d87f2d50dd` | **PASS** | — | PASS StackChan servo marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stackchan-servo` |
| 42 | stopwatch-vibration | m5stopwatch | v2.5.5 `0bcb9269f4` | **PASS** | — | PASS vibration marker rgb=(0,127,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stopwatch-vibration` |
| 43 | stopwatch-audio | m5stopwatch | v2.5.5 `0bcb9269f4` | **PASS** | — | PCM bytes=446464 samples=223232 nonzero=88194 peak_to_peak=11523 \| PASS StopWatch audio marker rgb=(0,127,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stopwatch-audio` |
| 44 | stopwatch-mic | m5stopwatch | v2.5.5 `0bcb9269f4` | **PASS** | — | PASS StopWatch mic marker rgb=(0,127,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stopwatch-mic` |
| 45 | atoms3r-lp5562 | m5atoms3r | v2.5.4 `c289f7df74` | **PASS** | — | PASS LP5562 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/atoms3r-lp5562` |
| 46 | atoms3r-ir | m5atoms3r | v2.5.4 `c289f7df74` | **PASS** | — | PASS NEC offset=0 address=0x56 command=0xa3 | #185 provenance | `.work/retest-20261106/peripheral-matrix/atoms3r-ir` |
| 47 | cardputer-adv-ir | m5cardputeradv | v2.5.4 `fe39163d55` | **PASS** | — | PASS NEC offset=0 address=0x56 command=0xa3 | #185 provenance | `.work/retest-20261106/peripheral-matrix/cardputer-adv-ir` |
| 48 | papercolor-ir | m5papercolor | v2.5.4 `ccffe79f97` | **PASS** | — | PASS NEC offset=0 address=0x56 command=0xa3 | #175 | `.work/retest-20261106/peripheral-matrix/papercolor-ir` |
| 49 | core2-peripherals | m5core2 | v2.5.4 `57868df3d1` | **PASS** | — | PASS serial markers: CORE2_PERIPHERAL_MAIN, CORE2_RTC 2026-10-22 06:07:08, CORE2_TOUCH, CORE2_PWR \| PASS Core2 peripherals marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/core2-peripherals` |
| 50 | core2-audio | m5core2 | v2.5.4 `57868df3d1` | **PASS** | — | PCM bytes=10240 samples=5120 nonzero=5111 peak_to_peak=46091 \| PASS Core2 audio marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/core2-audio` |
| 51 | core2-mic | m5core2 | v2.5.4 `57868df3d1` | **PASS** | — | PASS serial markers: CORE2_MIC_RESULT ok, CORE2_MIC_DRAW_COMPLETE ok \| PASS Core2 mic marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/core2-mic` |
| 52 | core2-power-monitor | m5core2 | v2.5.4 `57868df3d1` | **PASS** | — | PASS Core2 INA3221 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/core2-power-monitor` |
| 53 | stamplc-can | m5stamplc | v2.5.4 `cade08fdfb` | **PASS** | — | PASS StamPLC CAN marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stamplc-can` |
| 54 | stamplc-rs485 | m5stamplc | v2.5.4 `cade08fdfb` | **PASS** | — | PASS StamPLC RS485 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stamplc-rs485` |
| 55 | stamplc-buzzer | m5stamplc | v2.5.4 `cade08fdfb` | **PASS** | — | PCM bytes=382976 samples=191488 nonzero=24000 peak_to_peak=60855 \| PASS StamPLC buzzer marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stamplc-buzzer` |
| 56 | core2-imu | m5core2 | v2.5.4 `57868df3d1` | **PASS** | — | PASS Core2 IMU marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/core2-imu` |
| 57 | core2-axp192 | m5core2 | v2.5.4 `57868df3d1` | **FAIL** | PASS (attempt 1) |  | #185 provenance (#176 regression control) | `.work/retest-20261106/peripheral-matrix/core2-axp192` |
| 58 | stamplc-lm75 | m5stamplc | v2.5.4 `cade08fdfb` | **PASS** | — | PASS StamPLC LM75 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stamplc-lm75` |
| 59 | papercolor-rgb | m5papercolor | v2.5.4 `ccffe79f97` | **PASS** | — | WS2812 PASS expected=00ff00ff0000 offset=98 \| PASS PaperColor RGB marker rgb=(67,138,28) | #175 | `.work/retest-20261106/peripheral-matrix/papercolor-rgb` |
| 60 | stamplc-onboard-io | m5stamplc | v2.5.4 `cade08fdfb` | **PASS** | — | PASS StamPLC onboard IO marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stamplc-onboard-io` |
| 61 | cores3-aw9523-full | m5cores3 | v2.5.5 `5847a2bcae` | **PASS** | — | PASS CoreS3 AW9523 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/cores3-aw9523-full` |
| 62 | stopwatch-m5ioe1-full | m5stopwatch | v2.5.5 `0bcb9269f4` | **PASS** | — | PASS StopWatch M5IOE1 marker rgb=(0,127,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stopwatch-m5ioe1-full` |
| 63 | stopwatch-m5pm1-full | m5stopwatch | v2.5.5 `0bcb9269f4` | **PASS** | — | PASS serial markers: STOPWATCH_M5PM1_BUTTON_CFG, STOPWATCH_M5PM1_FIELDS, STOPWATCH_M5PM1_DONE PASS \| PASS StopWatch M5PM1 marker rgb=(0,127,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/stopwatch-m5pm1-full` |
| 64 | nesso-peripherals | esp32c6 | v2.5.4 `fcbd588fa9` | **PASS** | — | PASS Nesso peripherals marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/nesso-peripherals` |
| 65 | nesso-imu | esp32c6 | v2.5.4 `fcbd588fa9` | **PASS** | — | PASS Nesso BMI270 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/nesso-imu` |
| 66 | nesso-ir | esp32c6 | v2.5.4 `fcbd588fa9` | **PASS** | — | PASS NEC offset=0 address=0x56 command=0xa3 \| PASS Nesso IR marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/nesso-ir` |
| 67 | nesso-lora | esp32c6 | v2.5.4 `fcbd588fa9` | **PASS** | — | PASS Nesso SX1262 marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/nesso-lora` |
| 68 | nesso-buzzer | esp32c6 | v2.5.4 `fcbd588fa9` | **PASS** | — | PCM bytes=48128 samples=24064 nonzero=12866 peak_to_peak=65535 \| PASS Nesso buzzer marker rgb=(0,255,0) | #185 provenance | `.work/retest-20261106/peripheral-matrix/nesso-buzzer` |

## FAIL list (both observations kept)

| case | main observation | re-run observation | classification | candidate |
| --- | --- | --- | --- | --- |
| stackchan-peripherals | FAIL —  | FAIL —  | **infra** INFRA-LOAD | `candidates/stackchan-peripherals-before-frame-load.md` |
| core2-axp192 | FAIL —  | PASS — PASS Core2 AXP192 marker rgb=(0,255,0) | **infra** INFRA-LOAD,RECOVERED-ROUND2 | `—` |

## Additional observations / load analysis

### stackchan-peripherals (infra INFRA-LOAD)

Main observation and both serial re-runs (3/3, host load 7.5-13.5, competing round-3 QEMU guests) failed the observer precondition "before frame is blank: 0 non-black pixels"; in the same runs the after frame (captured after inputs+8 s) was non-black, i.e. the guest drew the UI later than the 3 s pre-input settle. Diagnostic control run of the identical guest/probe/runtime/firmware with only the observer settle increased (--wait 10, outside the matrix result) produced before.png with 645 non-black pixels, sha256 fc847f77d2de..., byte-identical to the before.png of the repair-phase PASS run in .work/issue-repair-20261105/final-peripheral-matrix/stackchan-peripherals/. This is a load-induced timing sensitivity of the tracked case settle, not a model/controller regression; lead decides whether to harden the fixture settle or file it.

- **serial re-run 2 (same command/runtime/firmware)** → status `FAIL`; evidence `.work/retest-20261106/peripheral-matrix/rerun2/stackchan-peripherals`

Recorded host load samples during the run (1-minute average): 14:55 9.06 5.79 4.07, 14:57 8.05 6.21 4.40, 15:00 13.50 9.44 6.05, 15:02 13.02 10.43 6.88, 15:04 9.65 10.17 7.27, 15:06 8.79 9.72 7.57

## Notes / limits

- Tracked runner and case definitions are unmodified; all scripts/artifacts live under `.work/retest-20261106/`.
- Repair validation is bound to the exact per-case firmware sha (`base_firmware_sha256` from the real partition table) and the repaired runtime sha; #177 SHA-bound replacements are selected only when the base sha matches.
- All FAIL observations and their re-runs are retained; a later PASS does not erase the first FAIL.
- Direct-QEMU results are virtual-device only; RF/optical/electrical/mechanical claims are out of scope. No Device Service session is used in this scope (session_id = N/A).

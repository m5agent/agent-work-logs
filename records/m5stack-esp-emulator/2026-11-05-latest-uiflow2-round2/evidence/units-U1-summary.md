# R2-U1 — remaining Unit batches on service 8901（latest firmware）

- generated_at: `2026-11-05T17:37:56.537004+08:00`
- 执行身份：virtual-device validation（QEMU + Device Service 8901），非物理硬件。
- runtime: `<repo>/.work/goals/2026-11-04-uiflow-full/runtime-build/build-xtensa/qemu-system-xtensa` sha256 `0e16a9bcd86b588dae6b3e3b523dfb8610a9eca37c50c141cce5f2ceb4612068`（canonical 41 层 Unit 链）
- 固件：cores3 `v2.5.5` sha256 `5847a2bcae33d6bb8942de1c3ae92295a8441b6a3424c78e444fc748c9508ded`（all U1 cases hosted on cores3）

## 覆盖与结果

- cases: **17** / planned 17
- PASS: **17**；PASS-AFTER-RERUN: **0**；FAIL: **0**；BLOCKED: **0**
- NOT RUN: （无）
- round2 复跑：未触发（round1 无 FAIL/BLOCKED）

| batch | cases | PASS | PASS-AFTER-RERUN | FAIL | BLOCKED | devices |
| --- | --- | --- | --- | --- | --- | --- |
| batch11 | 7 | 7 | 0 | 0 | 0 | cores3 |
| batch12a | 7 | 7 | 0 | 0 | 0 | cores3 |
| can_lorawan | 3 | 3 | 0 | 0 | 0 | cores3 |

## FAIL 清单

（无）

## BLOCKED（tracked runner expected-blocked / known-blocker）

（无）

## 每 case 身份摘要

| case | device | firmware | base sha | merged sha | session | status |
| --- | --- | --- | --- | --- | --- | --- |
| batch11/glass | cores3 | v2.5.5 | 5847a2bcae33 | a43c688ec157 | d40ce86f | PASS |
| batch11/lorawan-as923 | cores3 | v2.5.5 | 5847a2bcae33 | 7b63c7647345 | 497400fc | PASS |
| batch11/lorawan-eu868 | cores3 | v2.5.5 | 5847a2bcae33 | 298f800d9a5a | d83fe9e0 | PASS |
| batch11/rf433t | cores3 | v2.5.5 | 5847a2bcae33 | 757934681653 | 9772252e | PASS |
| batch11/rf433r | cores3 | v2.5.5 | 5847a2bcae33 | 11f011154e6e | dae28a5f | PASS |
| batch11/audioplayer | cores3 | v2.5.5 | 5847a2bcae33 | bc5c533c0d27 | 68172ade | PASS |
| batch11/fingerprint2 | cores3 | v2.5.5 | 5847a2bcae33 | 3ce377bb1aed | 508497e1 | PASS |
| can_lorawan/can | cores3 | v2.5.5 | 5847a2bcae33 | f0fadd3e266b | 742d720f | PASS |
| can_lorawan/mini-can | cores3 | v2.5.5 | 5847a2bcae33 | 2b47ffcf175d | 383c569c | PASS |
| can_lorawan/lorawan-us915 | cores3 | v2.5.5 | 5847a2bcae33 | bc5831caa789 | 6e0ede15 | PASS |
| batch12a/byteswitch | cores3 | v2.5.5 | 5847a2bcae33 | 8eb040d577b4 | 7eb7234b | PASS |
| batch12a/bytebutton | cores3 | v2.5.5 | 5847a2bcae33 | 62cefc444145 | 1ab6c41b | PASS |
| batch12a/step16 | cores3 | v2.5.5 | 5847a2bcae33 | 942fd4abc2fe | 95b98ed6 | PASS |
| batch12a/timerpwr | cores3 | v2.5.5 | 5847a2bcae33 | 3cc2ceb1c12f | 11a1769d | PASS |
| batch12a/mq | cores3 | v2.5.5 | 5847a2bcae33 | 512f7db29ea8 | 6d341309 | PASS |
| batch12a/8servos2-i2c | cores3 | v2.5.5 | 5847a2bcae33 | 87260bcd2888 | 1aa0450f | PASS |
| batch12a/cardkb2 | cores3 | v2.5.5 | 5847a2bcae33 | 646f6aabf71c | ca0f0c9a | PASS |

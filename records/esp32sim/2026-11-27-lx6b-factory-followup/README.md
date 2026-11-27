# LX6-B classic Stick factory follow-up

- Date `2026-11-27`
- Result `PARTIAL` virtual-device validation with both factory UI gates PASS
- Work type `code_change`
- Source esp32sim `m5/batch-lx6b` at `63f25e3147f84379d3fdd2dd076f3128d5b34d14`. [Branch commit](https://github.com/m5agent/esp32sim/commit/63f25e3147f84379d3fdd2dd076f3128d5b34d14)
- Environment native ESP32 simulator with mask ROM boot, pinned Arduino examples and original catalog images
- Issue or PR not applicable. This work follows the batch qualification review. [Previous qualification](https://github.com/m5agent/agent-work-logs/tree/a165414a20db7abb9b9eaa54f6ebe793a2d4e82f/records/esp32sim/2026-11-27-lx6b-stick)

## Result

Both original factory images now exercise the classic hardware buses through their application screens. The replay ran 85 compiled Arduino cases. 83 passed and two reproduced pinned library defects. Seven source cases still fail to compile. Both factory images and both device-local controller probes passed their declared functional checks.

- M5Stick printed `mpu9250 addr: 71`, drew the SH1107 factory text on G35 press and cleared it after release.
- StickT2 completed 64 VoSPI frames in each of three factory captures and rendered two synthetic scenes. BtnA changed that application from RGB to GRAY.
- Native and WASM Clippy passed. CoreS3 and Cardputer-ADV suites passed completely. Seven workspace failures match the earlier baseline.

## Files

- [Full per-case matrix and root causes](report.md)
- [Structured replay identity](run.json)
- [Regressions and independent controller readback](evidence/regression-summary.json)
- [M5Stick factory evidence](evidence/m5stick-summary.json)
- [StickT2 factory evidence](evidence/stickt2-summary.json)

## Limits

StickT2 absolute temperature readout remains partial. The synthetic images verify VoSPI, display and input. Physical calibration and exact-module CCI length readback were not run. The work record includes software and regression exceptions.

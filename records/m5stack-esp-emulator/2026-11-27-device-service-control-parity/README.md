# ESP Emulator Device Service control parity

- Date `2026-11-27`
- Result `PARTIAL` · virtual-device validation
- Work type `code_change`
- Source [ESP Emulator](https://github.com/m5agent/m5stack-esp-emulator), based on `5f3c4bd35fdc6f7fec4eddfcdb98420b95024d94`
- Runtime [esp32sim candidate a6216b68](https://github.com/m5agent/esp32sim/tree/a6216b68abda3af76f6f491f940fbf0e4e8a42f7)
- Environment macOS arm64, isolated Device Service, original merged firmware and checked-in UIFlow2 fixtures

Native Device Service verification covered modeled-state snapshots, live and final
Flash readback, restricted STA, SD read delivery counters and media presence.
Paired Arduino and UIFlow2 observations cover the cases in the evidence below.
The catalog migration and resident rollout are pending.

- [Engineering report and reproduction](report.md)
- [Per-device table](per-device.md)
- [Run manifest](run.json)
- [Binary and source identities](evidence/runtime-identities.json)
- [HTTP control evidence](evidence/http-control-summary.json)
- [Arduino trials](evidence/arduino-trial-summary.json)
- [UIFlow2 trials](evidence/uiflow2-trial-summary.json)
- [Additional checked-in UIFlow2 fixture trials](evidence/ui-matrix-summary.json)

Physical devices and complete reviewer jobs were NOT RUN in this milestone.

- [Merged milestone follow-up](follow-up-milestone.md)

- [Merged-pin per-device documentation observations](per-device-merged-oracles.md)
- [AtomU and Atom Echo candidate defaults and PaperColor readiness](classic-defaults-and-panel-readiness.md)
- [Expanded per-device defaults and qualified consumer paths](expanded-paired-qualifications.md)
- [Final pin and per-device paired documentation matrix](final-pin-doc-matrix.md)
- [Remaining exact consumer gaps and StickC Plus SE](default-routing-follow-up.md)

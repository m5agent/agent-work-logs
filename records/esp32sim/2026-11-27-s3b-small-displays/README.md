# ESP32-S3 small display board ports

2026-11-27 · PARTIAL · virtual-device validation

The native esp32sim port covers the original Cardputer, Dial, StickS3 and StopWatch. Each case is bound to the exact ROM booted firmware and native runtime used in its replay.

| Board | Passing cases including stock UIFlow2 |
| --- | ---: |
| cardputer | 11/11 |
| dial | 11/11 |
| sticks3 | 11/16 |
| stopwatch | 18/19 |

- [Fork branch](https://github.com/m5agent/esp32sim/tree/m5/batch-s3b)
- [Validation and replay](report.md)
- [Machine-readable result](run.json)
- [Hashes and individual verdicts](evidence/case-summary.json)
- [Follow-up on StickS3 wake and StopWatch audio power](followups/2026-11-27-power-paths/README.md)

The matrices cover digital behavior in a virtual device. RF, battery characteristics, motor mechanics and IR optical behavior were outside this execution.

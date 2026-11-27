# StickS3 wake and StopWatch audio power

2026-11-27 · PARTIAL · code change and virtual-device validation on macOS arm64

The follow-up reviews the pinned Arduino examples for I²C ownership, timer wake and speaker shutdown. Four StickS3 examples assign one pair of GPIOs to two I²C controllers. The direct five-second wake example arms the ESP timer and then shuts off its supply. The StopWatch model now resets and disconnects the ES8311 on power loss. The pinned rail-control example restores power before playing its nominally silent tone.

- [Original batch, including the first verdicts](../../README.md)
- [Follow-up report and reproduction](report.md)
- [Machine-readable record](run.json)
- [Bounded protocol and PCM evidence](evidence/summary.json)

The electrical and acoustic behavior on physical hardware was outside this execution. Physical consequences are inferred from the pinned driver code, the GPIO-matrix register definitions and the board schematics.

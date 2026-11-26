# Tab5 milestone 3

- Date `2026-11-26`
- Result `PARTIAL`, virtual-device validation
- Work type `code_change`
- Source [esp32sim at 284b61da](https://github.com/m5agent/esp32sim/commit/284b61da59c88209b3b37fc2b77ca23debd883d2)
- Environment macOS ARM64, P4 rev < 3 mask ROM, Tab5 ILI9881C/GT911 and separate ST7123 touch case

The original Arduino wake, station, scan and SNTP examples and the original Arduino USB SDK probe exercise guest hardware paths. SoftAP uses the documented commented AP block in a separate build. The speaker source copy remains a documented compilation defect.

- [Report](report.md) gives root causes, configuration and limits.
- [Execution manifest](run.json) binds case inputs, outputs and runtime identities.
- [Verdicts](evidence/verdicts-summary.ndjson), [guest and controller markers](evidence/guest-summary.txt) and [benchmark results](evidence/bench-summary.ndjson) are bounded evidence.
- [Reproduction](code/README.md) describes the build and matrix runner.

The record covers native emulation. Physical board and browser guest execution, RS485 data-plane behavior and external NTP access remain outside its passing results.

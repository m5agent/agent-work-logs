# NanoC6 and Nesso N1 native board replay

2026-11-27 · PARTIAL · code change · virtual-device validation

NanoC6 passed nine of 15 compiled Arduino cases. Thread discovery and
Zigbee network scanning worked. Thread attachment and Zigbee join and
binding remained open. Nesso N1 passed all 11 compiled Arduino cases,
including the paired LoRa replay. The twelfth Arduino example has a
documented compile defect. Both stock UIFlow2 v2.5.3 releases responded
to USB-Serial-JTAG and board inputs.

- [Batch source](https://github.com/m5agent/esp32sim/tree/c2734200d15670eecd990386f89d0883528dd2f1)
- [Replay and per-case results](report.md)
- [Source, firmware and execution identity](run.json)
- [NanoC6 replay and peer markers](evidence/nano-summary.json)
- [Nesso N1 replay and LoRa markers](evidence/nesso-summary.json)
- [Regression results](evidence/regression-summary.json)

The runs used the native ESP32-C6 CLI on macOS arm64. Physical
measurements and the ELF-backed BLE path were outside the executed
matrix. The fork contains the patches and replay code. The record
contains the derived summaries and hashes of raw artifacts.

[S3-A merge and combined regression](evidence/merge-s3a-summary.json)

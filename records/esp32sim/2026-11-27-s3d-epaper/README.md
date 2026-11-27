# ESP32Sim S3 e-paper boards

- Date `2026-11-27`
- Result `PARTIAL` virtual-device validation
- Work type `code_change`
- Source `m5/batch-s3d` at [`4e3ad5278436c00750b4846af3888096099936c7`](https://github.com/m5agent/esp32sim/tree/4e3ad5278436c00750b4846af3888096099936c7)
- Environment macOS arm64, native CLI with the ESP32-S3 mask ROM, pinned Arduino and original UIFlow2 images

## Result

Implemented four board models and validated guest-visible completion of ET047TC1, SSD1677 and ED2208 refreshes. All four original UIFlow2 images reached their offline home screen. Full device acceptance remains open.

| Board | PASS | FAIL | NOT RUN |
| --- | --- | --- | --- |
| paperdiy | 6 | 0 | 0 |
| papers3 | 6 | 1 | 2 |
| papermono | 5 | 2 | 19 |
| papercolor | 5 | 1 | 10 |

## Evidence

- CoreS3 15/15 and Cardputer-ADV 11/11 completed at their recorded simulator version.
- PaperMono exchange delivered six matching messages through loopback UDP. The receiver-only control stayed in listen mode without messages.
- Firmware and simulator SHA-256 values are in [run.json](run.json). The per-case results and reproduction outline are in [report.md](report.md).
- The archive contains bounded summaries and hashes for reproduction.

## Remaining acceptance

PaperDIY passed its six Arduino checks, USB-CDC REPL and independent stock button readback. The remaining boards need their outstanding peripheral and timing cases.

Follow-up checks for all four boards are in [followup-report.md](followup-report.md), with exact execution hashes in [followup-run.json](followup-run.json).

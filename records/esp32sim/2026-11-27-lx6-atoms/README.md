# Classic Atom family and shared ESP32 controllers

- Date 2026-11-27
- Result PARTIAL
- Work type code change
- Request LX6-A device-port assignment, no public issue
- Source [esp32sim batch](https://github.com/m5agent/esp32sim/tree/03b35b0f3f5880e4b00d1967c90e8e2c6f98241a)
- Environment native AArch64 macOS runner, ESP32 ECO3 mask ROM and SHA-pinned firmware

Atom Lite and both Matrix revisions passed the applicable docs and stock checks. AtomU and Echo reached UART0 REPL and passed button, RGB and converted PDM tests. Echo also replayed a 440 Hz tone through I2S1. Stock v2.5.4 startup on AtomU and Echo raised a missing M5Things import.

The evidence binds the runtime and firmware hashes to serial markers, LED frames and PCM captures. Physical measurements and browser execution were NOT RUN. Echo's three Arduino docs cases stopped at compilation.

[Detailed report](report.md) · [Run identities and results](run.json) · [Control markers](evidence/controls-summary.txt)

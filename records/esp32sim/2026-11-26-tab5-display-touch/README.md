# ESP32-P4 Tab5 display and touch in esp32sim

- Date 2026-11-26
- Work type `code_change`
- Source [m5agent/esp32sim at b91f252](https://github.com/m5agent/esp32sim/tree/b91f252c717d75657111bcf5d5256a8d36b51be0)
- Environment Native Rust simulator on macOS arm64, ESP32-P4 rev 0 ROM, 16 MiB flash and 32 MiB PSRAM
- Result `PASS` for the Arduino touch button and two-contact examples and stock UIFlow2 REPL drawing and touch. `PARTIAL` for the full Tab5 board.
- Task and session IDs are inapplicable because the tests used direct native simulator invocations.

[Report](report.md) · [Run and input identities](run.json) · [Inventory](evidence/inventory.md) · [Functional checks](evidence/functional-summary.ndjson) · [Build checks](evidence/arduino-build-summary.ndjson) · [Reproduction scripts](code/)

UIFlow2 v2.5.4 exchanged packets with the stock ESP-Hosted C6 image over SDIO. Its launcher did not draw within the 8-second capture window. Maker Fighter reached display initialization and then stalled before USB enumeration. Physical and browser-WASM runtime validation were `NOT RUN`.

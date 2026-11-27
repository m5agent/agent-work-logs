# esp32sim benchmark runtime follow-up

- Date — 2026-11-27
- Result — PARTIAL, virtual-device validation
- Type — code change and regression
- Source — [benchmark PR #288](https://github.com/m5agent/m5stack-esp-emulator/pull/288), [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188), [#226](https://github.com/m5agent/m5stack-esp-emulator/issues/226)
- Checkout — [esp32sim at 2fba23b0](https://github.com/m5agent/esp32sim/tree/2fba23b0305cc96a3bd9b9ccb78d0f3ed50523d8)
- Environment — macOS AArch64, local ESP mask ROMs, native CLI and Node.js WebAssembly ABI

The Classic Core scheduling change reduced Core2 stock UIFlow2 boot time while preserving the home framebuffer and serial output. In an isolated Device Service pair, the first complete home frame arrived at 5.40 s versus 30.24 s on baseline, with matching bytes. The standard release drew home in three of three runs within seven seconds. The frozen QEMU comparison reached the stock banner in three 24-second sessions and produced no complete home frame. Exact Tab5 stock firmware read its panel ID through the RX FIFO with the touchscreen disconnected. Tab5 USB-OTG read the requested sector from two different host images. The C6 reset probe preserved persistent flash over both software reset causes, and the original NanoC6 light responded to On and Off across a Zigbee leave and rejoin.

- [Report and reproduction](report.md)
- [Source, firmware and check manifest](run.json)
- [Trace and measurement summaries](evidence/)

Remaining edges include the original QEMU browser trap reproductions, original Maker Fighter MSC activity, C6 simultaneous Wi-Fi and 802.15.4, and full batch regression acceptance. Physical hardware was not run.

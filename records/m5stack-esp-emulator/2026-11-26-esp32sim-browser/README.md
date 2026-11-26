# ESP Emulator CoreS3 and Cardputer-ADV browser runtime

- Date 2026-11-26
- Result PARTIAL
- Work type code_change
- Source [Issue 242](https://github.com/m5agent/m5stack-esp-emulator/issues/242)
- Source version m5stack-esp-emulator `b2974d5139580a99f86c1478242a8ec695b1bdf4`
- Environment Chrome 158.0.8127.37 and source-built esp32sim WebAssembly on macOS

The static browser export booted both boards inside a cross-origin iframe without shared memory. Real firmware produced the display and input responses. Device detail pages ran their own guests. The mixed export exposed QEMU-WASM through the engine menu.

- [Report](report.md)
- [Structured record](run.json)
- [Sanitized browser evidence](evidence/browser-summary.json)

Production docs hosting, Device Service integration, physical devices and the full board example matrix were outside this run.

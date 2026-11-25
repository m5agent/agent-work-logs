# Cardputer-ADV signed portrait on locked browser QEMU 0049

- Date `2026-11-25`
- Result `PARTIAL` for issue #258, with the signed portrait fix verified
- Work type `issue`
- Source [Emulator issue #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258) and [the official IR sketch](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec)
- Base `m5stack-esp-emulator @ c4d4b3b376922caae1a19f4e49e78380fc6ec7da`
- Accepted source `b8d90de87113b3ea2e600213f97926193a6d785f`
- Environment Chromium `158.0.8127.37` on Apple silicon macOS and Emscripten `3.1.50`, Cardputer-ADV browser WASM virtual-device validation

## Result

The exact original IR firmware presents its text upright in the 135 × 240 portrait preview. The firmware still draws text beyond the short edges. Its USB Serial/JTAG address and two commands were unchanged. The original Display and Keyboard examples passed, and the tracked four-rotation guest passed 40 assertions on a separately built firmware from the same checked-in sources and pinned libraries. All four guests exited cleanly with no remaining workers.

NEC timing remains open. The locked production runtime has no waveform observer. The prior diagnostic A/B evaluated the original sketch and found zero complete frames within the fixed timing tolerance at both clock rates.

## Files

- [Report and reproduction steps](report.md)
- [Structured result](run.json)
- [Bounded evidence, firmware and runtime digests](evidence/locked-0049-portrait.summary.json)

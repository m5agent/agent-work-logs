# Cardputer-ADV IR example in browser QEMU

- Date `2026-11-25`
- Result `PARTIAL`
- Work type `issue`
- Source [`m5agent/m5stack-esp-emulator` issue #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258) and the [official IR NEC Arduino example](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec)
- Base [`m5stack-esp-emulator` at `a5a48ece`](https://github.com/m5agent/m5stack-esp-emulator/commit/a5a48eceee172be037fe7c742eeff5f529f778d5)
- Environment Apple silicon macOS, Chromium `158.0.8127.37`, Emscripten `3.1.50`, Cardputer-ADV browser WASM virtual-device validation

## Result

The unmodified example presented upside-down text on the locked `0044` runtime. A private candidate changed the portrait angle from `−90°` to `+90°` and the text became upright. The original sketch still clips text on its 135-pixel-wide portrait canvas. The guest emitted commands `0x34` and `0x35` at address `0x1111` through the simulated USB Serial/JTAG controller.

The same private WASM showed the actual GPIO44 LEDC envelope in both clock trials. The normal clock and the explicit divisor of 8 both produced zero of two frames within the unchanged NEC timing tolerance. The divisor reduced the timing errors and increased the host-observed interval between the guest USB messages from 1.25 s to 8.68 s. All four browser runs exited cleanly and left no workers.

## Evidence and reproduction

- [Report](report.md)
- [Structured work record](run.json)
- [Bounded virtual-device evidence and artifact identities](evidence/ir-virtual-device-summary.json)
- [Signed portrait C patch](patches/0001-cardputer-adv-signed-portrait.patch)
- [GPIO44 diagnostic C patch](patches/0002-cardputer-adv-gpio44-observation.patch)
- [Private browser validation patch](patches/0003-private-browser-validation.patch)
- [Unchanged strict NEC decoder](code/check_ledc_nec.py)

## Open checks

The portrait-only locked runtime, all four exact guest rotations on that runtime, and physical IR output require their own verification. The timing cause remains unconfirmed. This diagnostic build has no release or deployment.

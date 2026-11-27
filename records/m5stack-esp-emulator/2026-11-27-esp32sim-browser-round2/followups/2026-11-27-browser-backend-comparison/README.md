# Same-firmware Chrome backend comparison

- Date: 2026-11-27
- Result: PASS for the 13 paired fixed guest cases after synchronizing the Matrix RGB capture
- Work type: browser-WASM virtual-device validation and default selection
- Source: [PR #290](https://github.com/m5agent/m5stack-esp-emulator/pull/290)
- Environment: sequential Chrome 158 runs on macOS with the same exported workbench and exact guest SHA in each pair.
- Hardware validation: NOT RUN

The operator exercised the workbench input on each engine. Boot is runtime start to the guest ready marker. Input latency is host key or pointer dispatch to the guest count marker. Display equality compares the two RGB565 frames before and after input. Matrix compares two complete controller-derived 25-LED vectors. Every completed pair observed the actual Workers reach zero after Stop. Measurements are one host wall-clock sample per case.

| Device | Ready s esp32sim / QEMU | Count ms esp32sim / QEMU | Output matched | Selected default |
| --- | --- | --- | --- | --- |
| cardputer | 1.12 / 15.46 | 35 / 86 | RGB565 | esp32sim |
| sticks3 | 1.59 / 16.02 | 48 / 117 | RGB565 | esp32sim |
| stopwatch | 1.93 / 19.49 | 17 / 59 | Frame differed | QEMU-WASM |
| stackchan | 4.47 / 29.73 | 38 / 85 | Frame differed | QEMU-WASM |
| paperdiy | 7.74 / 76.31 | 303 / 10300 | Frame differed | QEMU-WASM |
| papermono | 5.71 / 15.84 | 1130 / 682 | Frame differed | QEMU-WASM |
| papercolor | 52.09 / 23.09 | 17027 / 2921 | RGB565 | QEMU-WASM |
| papers3 | 7.27 / 71.63 | 240 / 11537 | Frame differed | QEMU-WASM |
| atoms3r | 1.81 / 14.57 | 25 / 93 | Frame differed | QEMU-WASM |
| atom-matrix | 1.08 / 62.23 | 31 / 72 | 25 LEDs | esp32sim |
| atom-matrix-v11 | 1.08 / 60.27 | 39 / 68 | 25 LEDs | esp32sim |
| core2 | 7.99 / 81.16 | 84 / 436 | RGB565 | esp32sim |
| stickc-plus2 | 1.53 / 65.40 | 13 / 45 | Frame differed | QEMU-WASM |

PaperColor retained QEMU-WASM because its ready and count markers arrived sooner with matching frames. Profile configuration retains QEMU-WASM where the two observed RGB565 frames differed. Matrix initially failed the capture synchronization assertion. The repeat waited for the full controller output before pressing and passed independently for each revision.

Use an isolated mixed export and run `node platform/tests/test_public_browser_backend_comparison.mjs` with `M5_BROWSER_SITE` and an available Chrome. The comparison collector records the exact per-device merged Flash SHA, output digests, input and teardown.

[First attempt](evidence/comparisons-summary.json) · [Matrix repeat](evidence/comparisons-led-summary.json)

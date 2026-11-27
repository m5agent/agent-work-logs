# Browser runtime-gaps milestone and Pages delivery

- Date: 2026-11-27
- Result: PARTIAL. AtomU and classic Echo remain excluded and the remaining feature limits are listed by board.
- Work type: browser-WASM virtual-device validation
- Source: [PR #290](https://github.com/m5agent/m5stack-esp-emulator/pull/290)
- Hardware validation: NOT RUN

The release candidate incorporates [runtime-gaps milestone](https://github.com/m5agent/esp32sim/tree/9c0447e8e38d0bafc2f124e6e8b8cc5994d30eee) plus the browser patches on [the parity branch](https://github.com/m5agent/esp32sim/tree/c2329ebeb1f0a258eedecbab0dac7390aa31987f). The previous candidate and comparison receipts retain their earlier identities. Rust 1.99.1 built the pinned workspace from Git blobs. WASM SHA-256 is `e9c99a3addf8f57a9c62ed59a89fba932061e1a272ac267c5bebf62101b6991d`.

[Board-by-board results](report.md) · [Machine-readable execution](run.json) · [Evidence](evidence/)

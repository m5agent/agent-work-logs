# Integration and regression results

The S3-B merge combines the two board lists and preserves their flash, PSRAM and package selection. Cardputer uses the shared pin-based PDM route, with GPIO43 as clock and GPIO46 as data. The shared board trait retains S3-A camera clock handling and S3-B RMT and buzzer callbacks. StopWatch and Tab5 use one RX8130 RTC implementation.

| Board | Arduino PASS | DOCS-DEFECT | Stock UIFlow2 |
| --- | ---: | ---: | --- |
| cardputer | 10 | 0 | PASS |
| dial | 10 | 0 | PASS |
| sticks3 | 10 | 5 | PASS |
| stopwatch | 17 | 1 | PASS |

The Cardputer microphone replay distinguished two injected signals from silence and recovered 733 Hz in speaker output. The StopWatch power example restored the codec and amplifier rails through its own enable callback before 10 kHz PCM appeared. The StickS3 cases retained the five source-cited documentation defects, including the timer path that powers off the CPU without arming the PM1 timer.

CoreS3 passed 15/15 and Cardputer-ADV passed 11/11. Tab5 reported 25 PASS, one DOCS-DEFECT and two NOT RUN for cases without independent sketches. The Atom S3 family retained all reported per-board results, including the nine stock profiles across panel variants and 320×240 and 1600×1200 guest JPEG streams.

On the exact previous integration commit, the P4 Wi-Fi diagnostic assertion and six P4 goldens failed. The batch updated the assertion to match the existing P4 co-processor diagnostic. The same six golden failures remain on the merged tree. See the [gate manifest](evidence/gate-summary.json) for test names.

Both Clippy commands passed. Native release binaries used the repository profile. The workspace tests used the optimized release profile with LTO off, eight codegen units and debug symbols off. The runner used a default empty value when Bash 3.2 expands an empty switch array. Scripted inputs and firmware bytes were preserved.

```sh
cargo build --release --locked -p esp32sim --bin esp32sim --bin esp32sim-p4
cargo clippy --workspace --all-targets -- -D warnings
cargo clippy --release --target wasm32-unknown-unknown -p esp32sim-wasm --features jit-tests -- -D warnings
CARGO_PROFILE_RELEASE_LTO=off CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8 CARGO_PROFILE_RELEASE_DEBUG=0 \
  cargo test --release --workspace --no-fail-fast --locked -- --include-ignored --skip external_
```

Set `ESP32SIM_ROM_DIR` and run the repository Atom and S3-B runners with the prebuilt firmware and stock inputs listed in [run.json](run.json). Use the pinned [CoreS3 and ADV archive](https://github.com/m5agent/m5stack-firmware-archive) for the reference suites. Native S3 CLI SHA-256 is `03f8f14849fd3dca4e084c3a46ffc259ae1bff2acb83084087c89c88b306d4e4`. All output summaries contain normalized fixture names and hashes. Local paths, full logs and raw images were omitted.

Physical hardware and browser guest execution were NOT RUN. The pre-merge tree is the first parent of `20b6d40b1f6fdcef1ea4963828358bf6e54f807b`. Rollback in shared history would use a new revert commit of that merge, with the first parent as the mainline.

# Cardputer-ADV signed portrait verification on producer-locked 0049

The original Arduino IR example selected the portrait direction whose physical ST7789 transform differs from the workbench's fixed `−90°` fallback. Patch `0049` adds a read-only signed rotation readback derived from MADCTL and glass mounting. The workbench uses that result for the 3D model and flat frame and applies the inverse transform when converting flat coordinates. The controller still produces a 240 × 135 native framebuffer. [Issue #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258)

## Exact runtime and source

The complete producer build used source `7a74b3b9ee0c4fff3e1950f65021b7c57f392f11` with Emscripten 3.1.50 and lock SHA-256 `6ca9ff0938e76e84b659ff1a6abbd785c23842624742e5b88e86eb4384d718d1`. The build receipt asserts `all_objects_rebuilt=true`. The resulting WASM SHA-256 is `3110d2859c0eb8648a94c52200c6456f387379859f865c0d3f46058d50bd798f`. The candidate on the merged audio base is `b8d90de87113b3ea2e600213f97926193a6d785f`. Comparison with the producer source shows changes only in the backlog, ledger and generated project snapshot. The source lock, patch, runtime build and browser implementation are byte-identical. Both static exports had site manifest SHA-256 `5c53116f28894a0b6210167b3aecf52abaf77e9cb385da048901ceac85211495`. The browser used the final export under `/showcase/`.

## Original official examples

| Example | Result on exact 0049 WASM | Same-session evidence |
| --- | --- | --- |
| IR NEC | Signed portrait `PASS`, overall application `PARTIAL` | +90° displayed, 135 × 240 flat canvas and 240 × 135 native frame, four nonblack frames. The screenshot digest matched the upright frame from the private candidate. Text remains clipped in the original sketch. Actual simulated USB emitted address `0x1111`, commands `0x34` and `0x35`, 435 bytes and 42 packets. |
| Display | `PASS` | Two changing native RGB565 frames, 240 × 135 landscape at 0°, with 15 and 23 distinct colors from the original draw loop. |
| Keyboard | `PASS` | Twelve actual focus-bound controller down/up events. The expected `a`, `ab`, `abc`, Delete and Enter guest frames were observed in one session. |

The first Keyboard attempt stopped during artifact provenance preflight. The script ran from an earlier source checkout, so its `index.html` did not match the sealed export. It failed before Chrome, QEMU or user input started. The same driver bytes passed with the source checkout matching the export. Both outcomes remain in the receipt. [Official IR NEC](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec) · [Official Display](https://docs.m5stack.com/en/arduino/m5cardputer/display) · [Official Keyboard](https://docs.m5stack.com/en/arduino/m5cardputer/keyboard)

## Four-rotation regression

The guest used the unchanged tracked `tests/firmware/cardputer_input_orientation/src/main.cpp` with the pinned M5Cardputer, M5Unified, M5GFX and Arduino-IRremote revisions. This build used Arduino CLI 1.3.1 and M5Stack ESP32 board package 3.2.5, producing a new 8 MiB image SHA-256 `b2d1e4c2e03c44ca0e938237f265595c2d3eeccbcc0dbe58a154f1c7ac3747cd`. The historical PlatformIO binary was unavailable. This receipt applies to the new image.

| Guest rotation | Guest dimensions | Native dimensions | Signed angle, full and partial | Flat corners and partial 8 × 8 pixels |
| ---: | --- | --- | ---: | --- |
| 0 | 135 × 240 | 240 × 135 | −90° | PASS |
| 1 | 240 × 135 | 240 × 135 | 0° | PASS |
| 2 | 135 × 240 | 240 × 135 | +90° | PASS |
| 3 | 240 × 135 | 240 × 135 | 0° | PASS |

The regression verified the official ADV TCA8418 reader and real Enter edges that advance each rotation. It performed press and release on all 56 model keys, 55 direct PC bindings, combined Shift, aliases and Fn chords. All 40 assertions passed. Flat pointer inverse has a separate passing host contract. This case does not establish physical touchscreen behavior. Every guest ended through the workbench Stop control, with QEMU exit 0, iframe removal and all six observed workers closed. [Bounded guest input, framebuffer and cleanup evidence](evidence/locked-0049-portrait.summary.json)

## Reproduction

1. Run the repository QEMU source build with the exact `0049` source lock. Verify the full source-build receipt and WASM SHA. Export the Pages workbench locally under `/showcase/` with the matching QEMU and verified LittleFS runtime. Check the site manifest and browser source identities before loading a firmware.
2. Use local uploads of the unchanged official IR, Display and Keyboard sketches with the documented firmware hashes. For IR keep the original 4 MiB merged image, select Cardputer-ADV and inspect the native and flat frames and actual USB channel in the same session. For Display observe changes from the draw loop with the original landscape orientation. For Keyboard focus the model and send `a`, `b`, `c`, Backspace, Delete and Enter and require the expected guest results.
3. Assemble the four-rotation image from the unchanged tracked C++ source, the pinned libraries in the receipt and the `m5stack:esp32:m5stack_cardputer` Arduino CLI board profile with 8 MiB Flash, default 8 MiB partition scheme, CDC-on-boot disabled, Info log level and `-std=gnu++17`. Pass the independently verified resulting image and expected WASM SHA to `platform/tests/test_public_qemu_cardputer_input_display.mjs` with `M5_PUBLIC_SITE`, `M5_CARDPUTER_IMAGE`, `M5_CARDPUTER_IMAGE_SHA256`, `M5_CARDPUTER_WASM_SHA256` and `M5_CARDPUTER_OUT`. Bind any new build to its own firmware digest.
4. Stop each isolated guest and check the real worker counts before closing the browser. The CI-style host validation also passed 2,568 Python tests with 11 skips, all Node contracts and the catalog, profile, coverage, source-lock and snapshot checks.

## Boundary and rollback

This update qualifies signed portrait, the four exact guest paths and cleanup in browser QEMU. The original IR text still clips and physical hardware remains untested. Strict NEC timing on locked 0049 is `NOT RUN`. The previous diagnosed normal-clock and ÷8 timing results remain `FAIL`, tracked by issue #258. Production rendering is independent of the earlier private GPIO44 trace. Reverting the signed C readback and its matching browser presentation returns to the original orientation fallback.

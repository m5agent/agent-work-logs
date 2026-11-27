# Reproduction

The report pins source, firmware and executable SHA-256 identities. Use the
frozen runtime provisioning instructions from the tested service source and
create an independent loopback service with a separate control credential and
state directory. Use the same native binaries for the comparative arms.

```sh
export M5_SERVICE_FLASH_MODE=host-image
export M5_QEMU_XTENSA="$FROZEN_XTENSA"
export M5_QEMU_XTENSA_ROM_DIR="$FROZEN_XTENSA_ROMS"
export M5_QEMU_RISCV32="$FROZEN_C6"
export M5_QEMU_RISCV32_ROM_DIR="$FROZEN_C6_ROMS"
export M5_TAB5_DSI_EMULATOR="$FROZEN_TAB5_DSI"
export M5_TAB5_DSI_BOARD=gt911-ili9881c
export M5_TAB5_DSI_FIRMWARE_SHA256S=fb9df59f0f1a343c0200178d199e11de5627e076367ccca2a6d10754f0d3cff2,507f2aeeddfdd71357c019122cc76785b710ba24a4dc3adeb840d61c9ee8b1a7,2758b0c2a31585c150cc30fa9f8f6913e6e1634afd78e6bd3901d986296e8c8e
export M5_ESP32SIM_RUNTIME_DIR="$PINNED_ESP32SIM_INSTALL"
export M5_SERVICE_API_TOKEN_FILE="$CONTROL_FILE"
python3.12 platform/tools/serve.py "$TEST_PORT" --state-dir "$TEST_STATE"
```

Each row in [cases.json](cases.json) takes device, label, path to the merged
BIN and an optional device input. Fill those paths with the images matching
the [per-run raw input SHA-256](../evidence/native-summary.json). Keep
normalized Flash hashes separately, as the service pads some merged inputs.

```sh
python3.12 code/native.py "$TEST_ORIGIN" "$CONTROL_FILE" code/cases.json "$OUT" --window 8
python3.12 code/summarize.py "$RAW_ROOT" "$SUMMARY_OUT"
```

The native observations used an 8-second window for the stock matrix and
7 seconds for most examples, followed by device input where applicable.
The corrected DSI baseline used 12 seconds. The ADV input retry used 5
seconds before keyboard injection. See the report for sensor and firmware
boundaries. The benchmark requires Pillow and the same Python service
dependencies as the pinned source.

For browser tests serve the pinned mixed export using its project prefix.
Use Playwright with desktop Chromium 158 and a fresh context per arm.

```sh
node code/browser.mjs "$EXPORTED_SITE_URL" "$BROWSER_CASES" "$OUT"
M5_BROWSER_SITE="$EXPORTED_SITE_URL" M5_DOCS_FIRMWARE="$DOCS_FW" \
  M5_BROWSER_EVIDENCE="$OUT" node code/embedded.mjs cores3-touch cardputer-adv-keyboard
node code/browser-reset.mjs "$RESET_SITE_URL" "$COMPOSED_FIRMWARE" "$RESET_RECEIPT"
```

The boot list selects the first two firmware rows. For the embed test name
the same binaries `cores3/touch/touch.ino.merged.bin` and
`cardputer-adv/keyboard/keyboard.ino.merged.bin` beneath the firmware directory.
The reset inputs are built with the service repository's
`tests/browser-qemu/uiflow_workbench/compose.mjs` and the pinned LittleFS
assets used by the original reproductions.

The CoreS3 CPU control was built with ESP-IDF for ESP32-S3 from
[the accompanying source](main/main.c). The reported guest/host slope uses
the first and last complete `BENCH sec` records in the same API session.

# Tab5 virtual-device validation

## Implementation

The base was `76e8b35710d1879e073f73c4a03bd11b216fb95f` from esp32sim
`m5/main`. The board presets are `m5stack-tab5` (ILI9881C and GT911) and
`m5stack-tab5-st7123`. M5GFX 0.3.0 detects the board using GPIO 31/32
software I²C. The same devices are accessible by I2C1 after the guest
switches to the hardware driver.

The DSI host receives DBI packets and returns replies through its RX
FIFO. DPI scanout reads actual DW-GDMA descriptors and guest pixels through
the P4 memory map, raises completion and drives the panel. ESP-IDF
v5.4.1 and v5.5.4 `esp_lcd_panel_dpi.c` use that DMA engine for scanout.
The Arduino bootloader stalled while polling SAR1 conversion done during
entropy setup. The HP ADC model now latches completion on timer start
and implements the clear register. The model covers that digital
handshake. The Tab5 GPIO mapping also connects SDIO slot 1 to the C6.
[ESP-IDF v5.4.1 DPI source](https://github.com/espressif/esp-idf/blob/v5.4.1/components/esp_lcd/dsi/esp_lcd_panel_dpi.c) · [ESP-IDF v5.5.4 DPI source](https://github.com/espressif/esp-idf/blob/v5.5.4/components/esp_lcd/dsi/esp_lcd_panel_dpi.c)

## Executed checks

- Arduino 3.2.5, CLI 1.3.1, M5GFX/M5Unified 0.3.0, and English docs at
  `7219cc9286c39b463da84053deee40bc234625db`. Thirteen of fourteen
  standalone blocks compiled unchanged. The speaker block has
  `##include` on its first line and failed compilation. Power-output
  fragments are not standalone sketches.
- The GT911 button sketch shows “Button Released”, “Button Pressed” at
  scripted `(360,640)`, then “Button Released” after lift at 2.5 virtual
  seconds. The release frame reproduces the idle SHA-256.
- The ST7123 sketch displays `X:0160 Y:0400` and
  `X:0540 Y:0880` after two scripted contact slots.
- Both original UIFlow2 images accepted a REPL fill, rendered all
  921,600 pixels at RGB `(16,52,82)` after RGB565 quantization, and
  returned board 22, down at `(233,456)` and zero contacts after lift.
  In v2.5.3 the ILI9881C read requests returned page-one bytes
  `98 81 0c` through the DSI RX FIFO. The v2.5.4 run selected the
  original panel without issuing those reads.
- Stock v2.5.4 with ESP-Hosted C6 v2.12.6 initialized Wi-Fi and completed
  SDIO exchange, with 67 commands and 352 bytes to the P4, 237 from it
  at the C6 boundary. The 8-second capture had 453 DSI scans and a
  uniformly white visible buffer. Launcher UI and network connection
  are `PARTIAL`.
- Maker Fighter 1.4 printed its DSI framebuffer setup marker. The
  capture remained black after seven scans, with the trace ending in
  DMA2D/PPA activity. The run provides no USB host enumeration result.

Build, native and WASM Clippy, P4/S3 suites, and P4 USB MSC goldens passed.
Blank launch attempts, firmware-poll stalls and initial GT911 release
misses preceded these runs. No golden file was regenerated.

## Instruction counts and CPU time

Three interleaved native release runs per revision used the same ROM,
firmware and CLI inputs. The hello demos ran for 3 virtual seconds and
pocket-tank for 5. Console bytes and instruction counts matched per
workload. User CPU time is reported in seconds.

| Workload | Instructions by core | Baseline median CPU s | Tab5 branch median CPU s |
| --- | --- | ---: | ---: |
| hello | 2,949,740, 1,344,986 | 0.08 | 0.08 |
| c3-hello | 480,000,000 | 0.47 | 0.48 |
| c6-hello | 480,000,000 | 0.31 | 0.32 |
| p4-hello | 1,080,000,000, 0 | 2.59 | 2.59 |
| pocket-tank | 684,909,493, 873,140,214 | 12.20 | 12.73 |

[Benchmark summary](evidence/bench-summary.ndjson)

## Reproduce

Build `esp32sim-p4` with `cargo build --release --bin esp32sim-p4`.
Set `ESP32SIM_P4` to the executable and `ESP32SIM_ROM_DIR` to the mask ROM
directory from `tools/fetch-rom-elfs.sh`. Supply firmware matching
`run.json` in the corresponding paths under `code/firmware/`.
`build_docs.py` takes the English Arduino Tab5 Markdown directory and
an Arduino setup with the pinned core and libraries. Run
`code/run_all_tab5.sh`, then compile the macOS Vision helper with
`swiftc code/frame-text.swift -o frame-text` and run
`python3 code/check_tab5.py "$PWD/frame-text"`.

For the C6 run, split the stock merged C6 image at offsets 0, 0x8000,
0xd000 and 0x10000. Use bootloader bytes through 0x8000, the 0x1000
partition table, the 0x2000 OTA-data partition, and the app from
0x10000. Supply those files in
`--coproc c6:bootloader=...,ptable=...,otadata=...,app=...`. For
Maker Fighter, run the original image for six virtual seconds with
`--log-periph` on the original GT911 board profile.

## Follow-up and rollback

Implement DMA2D descriptor transfers and verify the PPA consumer with
Maker Fighter before testing its DWC2 HS host channels and HID traffic.
The separate device-mode MSC goldens stay in the regression set.
Then implement Tab5 I²S RX/TX and the codec endpoints, RTC and power
state, IMU injection, and SPI mode for the SD socket. GT911 currently
exports one contact. The DSI model currently uses a 60 Hz virtual
scan cadence. Physical behavior and browser-WASM execution are
`NOT RUN`. Revert the four Tab5 commits in reverse order to remove the
board support.

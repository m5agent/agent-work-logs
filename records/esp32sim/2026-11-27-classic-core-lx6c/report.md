# Classic Core family firmware replay

The Basic v2.7 and Core2 presets use the classic ESP32 GPIO, GP-SPI, I2C, I2S and DMA controllers. The Core2 preset represents v1.1. The `m5stack-core2-axp192` preset represents the original revision, and M5Unified reads each revision's ID through the same I2C bus.

The Basic panel needed a one-bit dummy phase before RDDID. The classic SPI CPU buffer wraps during long color fills, including the pinned M5GFX driver's 2,048-bit transactions. Core2's probe reads the selected ID4 parameter. Continuous Basic speaker DMA clocks out the high byte of each 16-bit word using two BCKs per sample.

All results below use **virtual-device validation**. The Basic stock replay uses 4 MiB because the selected catalog image is the Basic 4 MiB build. At 16 MiB that image selects resources associated with a different layout. The 4 MiB replay renders the launcher and applies buttons, with a file-open error for one launcher background asset.


### basic-v27

| Case | Status | Observation |
| --- | --- | --- |
| display | PASS | 320×240 framebuffer contains the filled background and visible color primitives |
| button | PASS | UART0 reports the three independent button edges and no idle or release edge |
| battery | PASS | Baseline and both injected states produced distinct LCD values |
| imu | DOCS-DEFECT | Fixture assignment points Basic at m5core/imu.md line 9, which targets Gray. K001-V27 Basic has no onboard IMU. |
| microsd | PASS | Two guest-decoded images, missing-card control and exact persisted WriteTest.txt |
| quickstart-longtextscroll | PASS | Two different 320×240 LCD frames during scrolling |
| wav | PASS | PCM capture at 96000 Hz contains the required tone(s) and the guest reached playback completion |
| speaker | PASS | PCM capture at 96000 Hz contains the required tone(s) |
| wakeup | PASS | Button input followed by deep-sleep reset and boot |
| stock | PASS | Stock UIFlow2 home screen and UART0 input round-trip |

### core2

| Case | Status | Observation |
| --- | --- | --- |
| display | PASS | 320×240 framebuffer contains the filled background and visible color primitives |
| button | PASS | Distinct input states and release observed in the guest frame |
| touch-1 | PASS | Distinct input states and release observed in the guest frame |
| touch-2 | PASS | Distinct input states and release observed in the guest frame |
| battery | PASS | Baseline and both injected states produced distinct LCD values |
| imu | PASS | Baseline and both injected states produced distinct LCD values |
| microsd | PASS | Two guest-decoded images, missing-card control and exact persisted WriteTest.txt |
| quickstart-scrollgraph | PASS | Two different 320×240 LCD frames during scrolling |
| wav | PASS | PCM capture at 48000 Hz contains the required tone(s) and the guest reached playback completion |
| wakeup | PASS | Button input followed by deep-sleep reset and boot |
| rgb_led | PASS | RMT drives ten uniform pixels in red, green and blue order |
| rtc | PASS | Guest identifies RTC, writes from sandboxed NTP and reads successive wall-clock values |
| vibration | PASS | 9 DLDO1 rail transitions, 600–3300 mV commanded |
| mic | PASS | On-card WAV contains silence then the two separately injected PDM-to-PCM tones |
| stock | PASS | Stock UIFlow2 home screen and UART0 input round-trip |

## Reproduction

Build the source commit in [run.json](run.json) using `CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16 cargo build --release -p esp32sim`. Run the repository's `tools/run-lx6-cores.py` once for each device with the compiled Arduino plan, stock images, classic mask ROM and FAT32 seed. The microSD PNGs came from the documented example links. Core2 used copies resized to the documented 320×240 because the published files are 960×540. The seed WAVs use 12 kHz mono signed 16-bit PCM, amplitude 14,000, 733 Hz for 6 seconds and 997 Hz for 12 seconds. The [replay summary](evidence/matrix-summary.json) binds each capture to the tree, binary, firmware, ROM and stimulus hashes.

The recording check uses the converted PDM receive path. RF, analog acoustics and physical motor behavior are outside this run. The classic BLE transport requires application ELF symbol hooks. An ELF matching the stock Core2 binary and a qualified stock NUS replay are **NOT RUN**.

The Core2 16 MiB flash and 8 MiB PSRAM probe exercised HIMEM pages 127, 128 and 255.

## Regression

CoreS3 passed 15/15 and Cardputer-ADV passed 11/11. Atom Lite and both Atom Matrix models passed. AtomU and Atom Echo reproduced the existing stock-launcher prompt failures. Their separate PCM and UART0 probes completed.

The workspace suite first returned 1,964 passes and 27 failures. Missing P4 firmware fixtures caused 26 failures and one P4 command expectation also failed. After installing the exact pinned fixtures and replaying the four affected test executables, the effective workspace tally was 1,984 passed and 7 failed. The seven remaining failure names match the LX6-A/S3-A baseline. They cover P4 goldens and the P4 Wi-Fi option expectation. Both Clippy commands passed. The latest affected library checks passed 623 tests. The classic and S3 hello runs preserved per-core instruction counts. [Regression receipts](evidence/regression-summary.json) To roll back, use the LX6-A base commit shown in [run.json](run.json).

The summaries retain hashes and behavioral assertions. Raw serial, frame captures and storage images remain local.

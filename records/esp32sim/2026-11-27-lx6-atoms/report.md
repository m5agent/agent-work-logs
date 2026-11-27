# LX6-A virtual-device validation

| Case | Atom Lite | Atom Matrix | Matrix v1.1 | AtomU | Atom Echo |
| --- | --- | --- | --- | --- | --- |
| button | PASS | PASS | PASS | — | — |
| rgb | PASS | PASS | PASS | — | — |
| ir_nec | PASS | PASS | PASS | — | — |
| imu | PASS | PASS | PASS | — | — |
| quickstart-logoutput | PASS | PASS | PASS | — | — |
| quickstart-echorest | — | — | — | — | DOCS-DEFECT |
| quickstart-playmusic | — | — | — | — | DOCS-DEFECT |
| quickstart-recordplay | — | — | — | — | DOCS-DEFECT |
| stock-startup | PASS | PASS | PASS | FAIL | FAIL |
| stock-repl | PASS | PASS | PASS | PASS | PASS |
| stock-layout | — | PASS | PASS | — | — |
| stock-mic | — | — | — | PASS | PASS |
| stock-speaker | — | — | — | — | PASS |

The Lite IMU sketch was executed as the no-sensor negative control. The Arduino IMU page targets Atom Matrix. Both Matrix revisions matched the two injected six-axis readings and the idle control. The MPU6886 and BMI270 were tested in separate board profiles on the same SDA25/SCL21 wiring. Red LED 8 and blue LED 20 appeared in the expected row-major positions on both Matrix variants. The exact v2.5.3 stock BIN is shared by the two Matrix profiles. Each had an independent run.

The v2.5.4 AtomU and Echo images raised `ImportError: no module named 'M5Things'` before the prompt on both the bare baseline and their named profiles. The stock-startup rows preserve that failure. The same images accepted UART0 probe commands. Both recorded silence and distinct buffers for 733 Hz and 1234 Hz fixtures. Echo's I2S1 WAV had 19,168 nonzero samples at 48 kHz, with a 440.042 Hz fundamental for the requested 440 Hz tone.

AtomU has no dedicated Arduino docs sketch in the pinned inventory. EchoRest failed compilation under the pinned package at BaiduRest.cpp line 175 because WiFiClient was undeclared. PlayMusic and RecordPlay failed in LED_DisPlay.h line 62 because boolean was undeclared. These three images could not be replayed.

## Shared controllers

The dual-core ESP-IDF fixture reported the UART0 baud change from 115201 to 230423, duty 256/1024 on LEDC, modeled DAC output on GPIO25 at 1656 mV, and timer wake with a retained RTC value. The virtual reset path went from SPI Flash boot to ROM download and back to the Arduino loop. GPIO12 NEC capture decoded aa55ff00 and a956fe01 through both the Arduino example and the RMT-driver fixture. Native classic tests exercised per-core interrupts, watchdogs, I2C transport, 64/128-clock converted PDM modes, TX DMA EOF, and SPI SD/MISO arbitration. The SD test used a fixture socket, with board-specific sockets owned by later batches.

The LX6-B and LX6-C batches can use the exact memory, PCM DMA and SPI SD support through source commit 201a52f0bbd86e42d500ae061296afb43db7d99b. S3-A subsequently published a separate MPU6886 polling model in the same module path at commit 5e87a7bb. Both board families use the 0x68 I2C part with signed configurable ranges. The merge needs a single model and a compatible sample setter. The LX6 board applies its axes in the board adapter.

The exact PSRAM capacities, 16 MiB Flash and higher HIMEM pages have an independent [memory record](../2026-11-27-lx6-memory/). Raw microphone PDM and continuous I2S-to-DAC playback were NOT RUN. The executed audio paths were converted PDM capture, I2S PCM playback to the Echo amplifier and the direct DAC register output. RMT RX was NOT RUN because the assigned IR circuits transmit. Browser and physical hardware were NOT RUN.

## Regressions

CoreS3 15/15, Cardputer-ADV 11/11, Cargo 1975 passed and 7 failed. Native and WASM Clippy passed with Rust warnings denied. The S3 and classic hello instruction counts matched their base runs exactly. The final build used LTO disabled under concurrent host load. The performance sentinel used guest instruction counts.

Six P4 golden cases fail on this base. The four ESP-Hosted report files expect the SDIO D0–D3 pin range. Both binaries print a list. Direct station replays on the original and candidate binaries produced identical serial output and instruction counts for both P4 revisions. The original raw-throughput RX and TX replays matched the candidate's reports and the committed console and instruction expectations. The two SMP hello guests also reached their guest markers and replayed with identical instruction counts on the original and candidate binaries. Both counts differ from the committed goldens. The P4 Wi-Fi STA option test also expects an older rejection message. Both binaries refuse P4 STA without a co-processor and emit the same diagnostic with exit status 2.

Earlier attempts are preserved in the local evidence. Initial Matrix output had opposite X/Z signs because the model held open-drain high during the GPIO probe. The first Echo TX run crashed when firmware read EOF from the register at 0x38. The model had written 0x40. Correcting these controller behaviors resolved the respective failures. The regression runners initially encountered Git LFS pointers and were rerun using SHA-256-verified objects. The first Cargo run reached 10 co-simulation failures due to an absent P4 fixture. The rerun used the repository's SHA-256-pinned P4 and MicroPython fixtures.

The [runner](https://github.com/m5agent/esp32sim/blob/03b35b0f3f5880e4b00d1967c90e8e2c6f98241a/tools/run-lx6-atoms.sh) accepts the compiled docs inventory, the fixed stock images and the ECO3 ROM. Build with `CARGO_PROFILE_RELEASE_LTO=false cargo build --release -p esp32sim`. Set `ATOM_PLAN_DIR`, `ATOM_STOCK_DIR` and `ESP32SIM_ROM_DIR` to the respective input directories and run `tools/run-lx6-atoms.sh target/release/esp32sim atom-matrix ./matrix-run` from the repository root. Change `atom-matrix` to the requested board and use a fresh output directory. [run.json](run.json) binds the 2026-11-27 results and the filtered serial summary to exact inputs. The evidence text retains test markers and hashes. Full serial output and workstation paths remain in local evidence. Return to the previous fork commit to roll back the board and controller changes.

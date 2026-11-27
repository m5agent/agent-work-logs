# S3-D e-paper verification follow-up

Virtual-device validation used runtime `751a0331dd16395330cea265c9ce40ae2008da48` and candidate branch `483a83cfdeda7b2a962eedf86c4010bae86f4252`. The per-run firmware, runtime, ROM, input and output hashes are in [followup-run.json](followup-run.json).

The ET047TC1 scan output latches an image after a powered waveform sequence. SSD1677 and ED2208 keep the visible frame during BUSY and apply completed updates in four-level grayscale and six-color output respectively. The service stream returned an all-white startup frame and a completed stock home image on each of the four boards. Each inherited Unix-socket session exited normally.

## Case matrix

### PaperDIY

6/6 documentation cases passed. Its published milestone is `4e3ad5278436c00750b4846af3888096099936c7`.

| Case | Verdict | Observation |
| --- | --- | --- |
| button | PASS | Each action changed the frame relative to the no-input control |
| display-1 | PASS | Completed grayscale frame with expected swatch ordering |
| display-2 | PASS | Each action changed the frame relative to the no-input control |
| m5pm1 | PASS | Timed restart and shutdown observed against a running control |
| microsd | PASS | Guest rendered SD media while the no-card control did not |
| quickstart-longtextscroll | PASS | Two completed nonuniform frames show the scroll changing |

Stock UIFlow2 2.5.4 passed its home-screen, USB CDC REPL and input checks. Both active and idle sessions returned the REPL arithmetic result. The idle session reported no input events.

### PaperS3

9/9 documentation cases passed. Its published milestone is `d6c4326f934887a2460d3c09379586dfc6568a08`.

| Case | Verdict | Observation |
| --- | --- | --- |
| battery | PASS | 3500 and 4200 mV, 4000 mV control |
| buzzer-1 | PASS | PCM contains 8 ordered tones and 2 silent gaps |
| buzzer-2 | PASS | PCM contains 6 ordered tones and 2 silent gaps |
| imu | PASS | Two injected IMU states and the stationary control match the axis readouts |
| rtc | PASS | Sandbox NTP, BM8563 calendar progression, and a changed clock screen |
| sdcard | PASS | Two seeded PNGs displayed and the exact WriteTest.txt bytes persisted |
| touch | PASS | Guest reported two points and silent no-input control |
| wakeup | PASS | Original loop resumed after 5.000 s of RTC timer sleep |
| quickstart-bargraph | PASS | White markers and quantized bars animate over a black background |

Stock UIFlow2 2.5.4 passed its home-screen, USB CDC REPL and input checks. Both active and idle sessions returned the REPL arithmetic result. The idle session reported no input events.

### PaperMono

25/26 documentation cases passed.

| Case | Verdict | Observation |
| --- | --- | --- |
| battery | PASS | PM1 read 3678/4200 mV vs 3900 mV baseline; gated IP2315 reported charging with VIN |
| button | PASS | BtnA and BtnB changed the visible status relative to the idle prompt |
| buzzer | PASS | PCM contains 3 ordered tones and 2 silent gaps |
| display-1 | PASS | Four quantized levels and white early control |
| display-2 | PASS | Two touch-selected display modes yielded completed frames distinct from idle |
| imu | PASS | Both inputs changed the visible measurement relative to the control |
| lora-1 | PASS | SX1262 peer read 4 exact payloads; disconnected control read none |
| lora-2 | PASS | SX1262 peer read 4 exact payloads; disconnected control read none |
| m5pm1_m5ioe1-1 | PASS | PM1 timer arm produced a power-on reset and a running guest |
| m5pm1_m5ioe1-2 | PASS | Wake source restored the simulated power rail and restarted the guest |
| m5pm1_m5ioe1-3 | PASS | PM1 IRQ and the guest wake status matched the input |
| m5pm1_m5ioe1-4 | PASS | Wake source restored the simulated power rail and restarted the guest |
| m5pm1_m5ioe1-5 | PASS | PM1 IRQ and the guest wake status matched the input |
| m5pm1_m5ioe1-6 | PASS | IOE1 W initialized, PM1 LoRa rail enabled, antenna/reset/NFC/LED latches toggled |
| mic | PASS | Guest microphone RMS tracks both input amplitudes and silence ([1138.7, 4562.3, 0.0]) |
| microsd | PASS | SDMMC reads produced the seeded JPEG bars; no-card control stayed on its status screen |
| nfc-1 | PASS | Guest read both programmed UIDs through ST25R3916 IRQ/FIFO and displayed the results |
| nfc-2 | PASS | Guest read both programmed UIDs through ST25R3916 IRQ/FIFO and displayed the results |
| nfc-3 | PASS | Guest wrote and read exact URI and text records on both tags through ST25R3916 |
| nfc-4 | DOCS-DEFECT | nfc_4.ino calls units.begin() before enabling NFC power through IOE1 GPIO4 |
| rgb_led | PASS | The installed LED channels followed the documented sequence |
| rtc-1 | PASS | Guest set August 18, 2026, read the advancing RX8130 time and rendered it |
| rtc-2 | PASS | NTP synchronized RTC, guest read back advancing time, and idle control stayed offline |
| touch | PASS | Touch markers at (60,120) and (190,320), then the untouched frame after both releases |
| wakeup | PASS | Button A resumed from light sleep and Button B rebooted from deep sleep, both after five seconds |
| quickstart-bargraph | PASS | White markers and quantized bars animate over a black background |

Stock UIFlow2 2.5.3 passed its home-screen, USB CDC REPL and input checks. Both active and idle sessions returned the REPL arithmetic result. The idle session reported no input events.

### PaperColor

14/16 documentation cases passed.

| Case | Verdict | Observation |
| --- | --- | --- |
| battery | PASS | Guest reported 3678 mV unplugged and 4200 mV plugged against baseline |
| button | PASS | Guest reported three injected buttons and no control presses |
| display | PASS | All six colors after refresh and white early control |
| ir_nec | DOCS-DEFECT | IRremote send feedback drives the built-in RGB LED alias on the same GPIO48 |
| m5pm1-1 | PASS | PM1 timer arm produced a power-on reset and a running guest |
| m5pm1-2 | PASS | Wake source restored the simulated power rail and restarted the guest |
| mic | PASS | Both injected frequencies survive microphone recording and playback |
| microsd | PASS | Guest rendered SD media while the no-card control did not |
| program | PASS | Completed frame matches the six-band PAPER COLOR quickstart artwork |
| rgb_led | PASS | The installed LED channels followed the documented sequence |
| rtc-1 | PASS | Guest set the calendar and observed it ticking |
| rtc-2 | PASS | NTP synchronized RTC, guest read back advancing time, and idle control stayed offline |
| sht40 | DOCS-DEFECT | sht40.ino uses Wire on the same pins M5.update() routes to the internal controller |
| speaker | PASS | PCM contains 3 ordered tones and 2 silent gaps |
| wakeup-1 | PASS | Button A armed the timer and the device restarted five seconds later |
| wakeup-2 | PASS | PM1 timer arm produced a power-on reset and a running guest |

Stock UIFlow2 2.5.3 passed its home-screen, USB CDC REPL and input checks. Both active and idle sessions returned the REPL arithmetic result. The idle session reported no input events.

## Root causes and shared code

- PaperS3's original 3.08-second interruption came from a watchdog reset. The ESP32-S3 RTC slow-clock timer now suspends both cores and resumes the original context after 5.000 seconds. PaperMono also exercised the separate deep-sleep reset path.
- PaperMono uses the S3-B M5PM1/IOE1 implementation and the S3-C ST25R3916 model. The board wires actual expander latch bits, motion IRQ, PM1 power state and the gated IP2315 charge register. NFC-A reader traffic goes through IRQ, anticollision, FIFO and Type 2 storage. SX1262 is shared with the Cardputer-ADV CAP implementation and uses loopback UDP for packet acceptance.
- PaperColor shares the PWM-envelope NEC decoder with Cardputer-ADV. Timing, carrier range and the command checksum are checked on GPIO48. The original `ir_nec.ino:101–102` configures feedback and IR on that shared GPIO through Arduino's RGB alias. The untouched official build emitted 24-bit RGB RMT submissions and zero accepted NEC frames. The diagnostic build added `NO_LED_SEND_FEEDBACK_CODE` before including IRremote. That replay returned PASS with 66 accepted NEC frames, including commands 0x34 and 0x35. The next completed ED2208 frame showed 0x35 at the 84-second capture.
- The shared SHT40 now NACKs reads until its 8.3 ms high-precision conversion is ready. The original `sht40.ino:49,60` uses controller 0 on the shared internal pins and runs `M5.update()` through controller 1 before measuring. The first probe acknowledged. After the PM1 access controller 0 lost its pin route, and the subsequent address write and read NACKed before the command reached the sensor. The exact-FQBN single-controller diagnostic replay returned PASS.
- PaperMono `nfc_4.ino:101–118,137–152` omitted the IOE1 GPIO4 power enable, which caused repeated address NACKs before target initialization. The powered diagnostic reached the guest emulation-ready message. Reader activation and external NDEF readback remain NOT RUN because no reader fixture is available.

## Reproduction and regression

All four exact Arduino FQBN smoke builds used M5Stack 3.3.10 and selected their expected M5GFX panel constructor in the guest. The full matrix remains bound to the lockfile's 3.2.5 firmware; PaperDIY, PaperMono and PaperColor used the PaperS3 FQBN in that matrix. The official 3.3.10 PaperColor IR and temperature retakes and PaperS3 bargraph replay are recorded separately.

Build the native simulator with `cargo build --locked --release -p esp32sim --bin esp32sim`. Select the appropriate `tools/run-paper*-docs.sh` with the built simulator, its pinned firmware directory and a fresh result directory. Pass `--source`, `--rom-dir` and the appropriate FAT32 `--sd` fixture. Use `--case stock --stock` to verify a matching stock binary. Run `python3 tools/check-paper-docs.py OUT` against each receipt. The full matrix includes the controller outputs, paired stimuli and idle runs. Use private writable SD copies and a lossless PNG fixture for PaperS3/Color. PaperMono uses a 240×160 baseline JPEG named `PaperMonoTest.jpg` with seven luminance bands.

CoreS3 15/15 and Cardputer-ADV 11/11 passed on the candidate runtime. Native and WASM Clippy passed. Workspace tests reported 1901 passed, one failed and 117 ignored. The failure is the inherited P4 Wi-Fi co-processor diagnostic-text assertion, reproduced on the unmodified base. The shared S3, C3 and C6 instruction-count sentinels preserved their counts and console digests.

Earlier host timeouts and device failures remain in the original receipts. Every selected run reached its configured guest horizon. Observed throughput ranged from 7.2 to 147.6 million retired guest instructions per wall second under concurrent host load. The PaperColor SD capture ran to 130 guest seconds to retain the second completed ED2208 refresh. The longest compute-bound example was the PaperColor PM1/RTC case. It retired 25.7 billion guest instructions over its 112-second acceptance horizon.

Validation covers digital panel output, the bus/controller interfaces, virtual NEC timing and LoRa loopback payloads. Physical contrast, pigment waveforms, optical IR, RF and power measurements were outside this run. For rollback, the PaperS3 and PaperDIY milestones remain at `d6c4326f934887a2460d3c09379586dfc6568a08` and `4e3ad5278436c00750b4846af3888096099936c7`.

BRANCH m5/batch-s3d @ 483a83cfdeda7b2a962eedf86c4010bae86f4252, regression CoreS3 15/15, ADV 11/11, cargo test 1901 passed

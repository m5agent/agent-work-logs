# ESP32-S3 e-paper batch

PARTIAL virtual-device validation on `m5/batch-s3d`. Published PaperDIY milestone `4e3ad5278436c00750b4846af3888096099936c7`.

## Panel and board detection

All four pinned Arduino display or quickstart ELFs reached their intended M5GFX constructor on the final runtime. PaperDIY, PaperMono and PaperColor digital display frames match the layout of the official example photos. PaperS3 sent actual GT911 coordinates through its I2C path.

- PaperDIY and PaperS3 use LCD_CAM I80 source data and GPIO gate/latch strobes.
- PaperMono uses timed SSD1677 RAM writes and mode-dependent four-level grayscale refresh.
- PaperColor uses timed ED2208 RAM writes, partial windows and the six-color palette.

## Case matrix

Every pinned case was attempted on the first candidate. NOT RUN denotes an incomplete behavior oracle even where the firmware process ran. Exit 124 is a host timeout.

### paperdiy

| Case | Status | Observation | Source |
| --- | --- | --- | --- |
| button | PASS | Each action changed the frame relative to the no-input control | `04017ae6` |
| display-1 | PASS | Completed grayscale frame with expected swatch ordering | `04017ae6` |
| display-2 | PASS | Each action changed the frame relative to the no-input control | `04017ae6` |
| m5pm1 | PASS | Timed restart and shutdown observed against a running control | `04017ae6` |
| microsd | PASS | Guest rendered SD media while the no-card control did not | `04017ae6` |
| quickstart-longtextscroll | PASS | Two completed nonuniform frames show the scroll changing | `04017ae6` |

Stock UIFlow2 2.5.4 reached its offline home screen. USB-CDC REPL PASS. Stock input PASS. Input readback uses the board input API over USB-CDC.

### papers3

| Case | Status | Observation | Source |
| --- | --- | --- | --- |
| battery | PASS | Guest displayed 3500 mV and 4200 mV for the two injected ADC levels. Control displayed 4000 mV | `b9998637` |
| buzzer-1 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| buzzer-2 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| imu | PASS | Two distinct vectors reached the guest display. Control displayed the stationary vector | `b9998637` |
| rtc | PASS | Virtual AP provided DHCP and one NTP reply. The final guest frame showed matching RTC and ESP32 UTC | `04017ae6` |
| sdcard | PASS | The guest reported a successful write and two PNG files, and rendered fixture media. The no-card control reported no card | `b9998637` |
| touch | PASS | Guest reported two points and silent no-input control | `b9998637` |
| wakeup | FAIL | Sketch requested 5 s of light sleep. Consecutive loop markers bracketed an approximately 3.08 s pause before execution resumed | `04017ae6` |
| quickstart-bargraph | PASS | Completed moving grayscale bargraph matched the quickstart example appearance | `b9998637` |

Stock UIFlow2 2.5.4 reached its offline home screen. USB-CDC REPL PASS. Stock input PASS. Input readback uses the board input API over USB-CDC.

### papermono

| Case | Status | Observation | Source |
| --- | --- | --- | --- |
| battery | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| button | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| buzzer | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| display-1 | PASS | Four quantized levels and white early control | `b9998637` |
| display-2 | NOT RUN | Frame captured; case-specific layout/action oracle pending | `b9998637` |
| imu | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| lora-1 | PASS | Six matched guest payloads through SX1262 and loopback UDP. No data in receiver-only control | `04017ae6` |
| lora-2 | PASS | Six matched guest payloads through SX1262 and loopback UDP. No data in receiver-only control | `04017ae6` |
| m5pm1_m5ioe1-1 | NOT RUN | Host timeout before the guest acceptance horizon | `b9998637` |
| m5pm1_m5ioe1-2 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| m5pm1_m5ioe1-3 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| m5pm1_m5ioe1-4 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| m5pm1_m5ioe1-5 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| m5pm1_m5ioe1-6 | FAIL | Guest reported an initialization or peripheral error | `b9998637` |
| mic | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| microsd | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| nfc-1 | FAIL | The 4-byte fixture completed selection. The independent 7-byte fixture completed zero selections | `04017ae6` |
| nfc-2 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| nfc-3 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| nfc-4 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| rgb_led | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| rtc-1 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| rtc-2 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| touch | PASS | Two visible touch-coordinate readbacks, full 96,000-byte partial update payloads and unchanged no-input control | `04017ae6` |
| wakeup | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `b9998637` |
| quickstart-bargraph | PASS | Two completed frames at 7 s and 10 s show different grayscale bar positions | `04017ae6` |

Stock UIFlow2 2.5.3 reached its offline home screen. USB-CDC REPL PASS. Stock input PASS. Input readback uses the board input API over USB-CDC.

### papercolor

| Case | Status | Observation | Source |
| --- | --- | --- | --- |
| battery | NOT RUN | Host timeout before the guest acceptance horizon | `e078fa72` |
| button | PASS | Guest reported three injected buttons and no control presses | `e078fa72` |
| display | PASS | All six colors after refresh and white early control | `e078fa72` |
| ir_nec | NOT RUN | Host timeout before the guest acceptance horizon | `e078fa72` |
| m5pm1-1 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `e078fa72` |
| m5pm1-2 | NOT RUN | Host timeout before the guest acceptance horizon | `e078fa72` |
| mic | NOT RUN | Host timeout before the guest acceptance horizon | `e078fa72` |
| microsd | PASS | Guest rendered SD media while the no-card control did not | `e078fa72` |
| program | PASS | The pinned quickstart drew the PAPER COLOR title and quantized panel swatches | `e078fa72` |
| rgb_led | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `e078fa72` |
| rtc-1 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `e078fa72` |
| rtc-2 | PASS | Guest joined the virtual AP, completed SNTP and read the synchronized time back from RX8130 | `b9998637` |
| sht40 | FAIL | Probe ACK followed by NACK on the measurement write and read. No sensor samples reached the guest | `e078fa72` |
| speaker | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `e078fa72` |
| wakeup-1 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `e078fa72` |
| wakeup-2 | NOT RUN | Firmware replayed; case-specific behavior oracle pending | `e078fa72` |

Stock UIFlow2 2.5.3 reached its offline home screen. USB-CDC REPL PASS. Stock input PASS. Input readback uses the board input API over USB-CDC.

## Regression

- CoreS3 15/15 and Cardputer-ADV 11/11 used the pinned firmware digests. The candidate runtime is `04017ae6`.
- Shared device tests passed 70/70 with the SX1262 identity fix. The S3 DMA subset passed 59/59 and M5 PMIC/IOE tests passed 8/8. Native and WASM Clippy passed on the current candidate.
- Workspace release suite on the milestone runtime had 1900 passes and 1 failure. The same P4 CLI assertion failed against the base under the exact baseline executable. The first optional ignored-test run also exposed missing P4 fixture files, subsequently restored and verified by hash.
- The S3, C3 and C6 hello sentinels reproduced their baseline instruction counts and console hashes at the captured horizon.

## Remaining acceptance

- PaperDIY timed PMIC power cycling passed. The other board-specific power-key, wake and RTC alarm paths remain open.
- USB-CDC ran the REPL arithmetic on all four original UIFlow2 images. The stock firmware read back the board inputs over USB-CDC. These probes used the board API after the home screen.
- Full PaperMono NFC-A read/write and card emulation, microphone, buzzer, RGB and native SD cases still need case-specific acceptance evidence.
- The PaperColor SHT40 example received an initial ACK before the subsequent measurement transfer NACK. There were zero guest samples. The sensor command and CRC unit tests passed.
- PaperDIY passed all six Arduino cases and stock input/REPL, then the branch milestone was pushed. The other three full case matrices remain open.

The data file records exact firmware, panel capture and runner hashes. Matrix subdirectories retain run commands and earlier failures.
The source can be rebuilt with `cargo build --locked --release -p esp32sim --bin esp32sim`. Use the four `tools/run-paper*-docs.sh` wrappers with the pinned firmware and mask ROMs.

## Implementation and rollback

The source base is `3e90d09bd31b5658d8dd2b6fc5d820da5f293489`. M5GFX revision `28d47949` and M5Unified revision `96576a14` define the probed devices, bus wiring and guest command paths. The Arduino firmware inputs remained pinned. Device Service transport probes used an inherited Unix socket and terminated their own local processes. They did not modify a running service.

The refresh models update a retained framebuffer on completed waveform or controller refresh. The SSD1677 and ED2208 BUSY signal polarities follow their respective drivers. The LoRa probe required the SX1262 identity register used by the pinned RadioLib driver. Adding the register allowed the same compiled sender and receiver to initialize and exchange packets. The SHT40 guest measurement fails in the subsequent I2C transaction. Its failure has not been isolated to the guest or the SoC route.

The PaperDIY milestone is on the batch branch. This record covers native emulator execution and the private transport probe. Rollback uses the pinned source base and its corresponding runtime.

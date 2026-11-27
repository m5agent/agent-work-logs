# S3-C completion replay

Branch commit `198c258aa196c0fad4391019ed0215cd6ce7d11e`. Runtime built from `f4eb46d1882da66186b6c1c553741eb8e10b84fa` with SHA-256 `8934d8c97fafbddf3a1ee782eba51908c0be3f8beb521d675bf592a2cca43277`.
This native virtual-device replay covers both board matrices, stock launcher and REPL, and the reference-board regressions.

## stamplc

1 DOCS-DEFECT. 13 PASS.

| Example | Result | Observation |
| --- | --- | --- |
| button | PASS | guest rendered all three button labels compared with the untouched screen |
| buzzer | PASS | GPIO44 LEDC produced 523, 659 and 880 Hz tones at 50 ms |
| can | PASS | TWAI TX and extended-ID peer reply with eight matching payload bytes |
| display | DOCS-DEFECT | Pinned display.md line 7 snippet calls Display as a field |
| input_output-1 | PASS | guest toggled all four modeled relay outputs |
| input_output-2 | PASS | zero-input control and two mapped AW9523 input patterns |
| modbus-1 | PASS | three Modbus master writes echoed over UART with mapped relay changes |
| modbus-2 | PASS | guest slave-peer exchange on RS485 including coils and input registers |
| rgb_led | PASS | all five requested GPIO-expander RGB states |
| rtc | PASS | guest set RX8130 calendar and read advancing time |
| sd_card | PASS | SPI SD guest writes and reads test.txt, with no-media control |
| sensor | PASS | three distinct LM75B and INA226 readings via guest I2C |
| quickstart-display | PASS | multicolor drawing over ST7789 SPI within the 240×135 crop |
| stock | PASS | stock UIFlow2 home visible after input and USB CDC REPL round-tripped |

## stackchan

1 DOCS-DEFECT. 26 PASS.

| Example | Result | Observation |
| --- | --- | --- |
| battery | PASS | two injected INA226 voltage and load readings on LCD |
| button | PASS | AXP2101 PMIC key produces rendered Btn PWR |
| camera | PASS | two distinct camera frames with VSYNC and zero dropped data |
| display | PASS | guest-drawn multicolor circles and rectangles |
| imu | PASS | two distinct BMI270 accelerometer and gyro readings on LCD |
| ir_nec | PASS | GPIO carrier delivered two valid NEC frames |
| ltr553 | PASS | two distinct LTR553 ranges and a no-stimulus control |
| mic | PASS | I²S mic recording played back distinct 733 Hz and 548 Hz signals, with silence control |
| nfc-1 | PASS | guest identifies and reactivates two Type 2 tags, with a no-tag control |
| nfc-2 | DOCS-DEFECT | Pinned nfc.md line 205 snippet leaves touch-button height at zero. BtnA requires raw y ≥ 240 and StackChan's FT6336 range ends at 239. |
| nfc-3 | PASS | virtual NFC reader selects the firmware tag and checks two NDEF memory reads |
| nfc-4 | PASS | two authenticated Classic tags with single-block and cross-sector write/readback |
| nfc-5 | PASS | guest formats and writes a synthetic Type 2 tag, then reads the NDEF URI |
| nfc-6 | PASS | two Classic value block flows demonstrate decrement, increment denial and permitted increment |
| pic | PASS | file reads are visible in the framebuffer and use SPI SD |
| rgb | PASS | PY32 RGB565 LED refresh observed across the twelve pixels |
| rtc | PASS | guest associates with virtual AP, consumes NTP and draws clock |
| sdcard | PASS | file reads are visible in the framebuffer and use SPI SD |
| servo-1 | PASS | touch saves two SCSCL encoder positions and restores them after displacement |
| servo-2 | PASS | top touch drives 45° pitch and then 90° yaw using serial servos |
| speaker | PASS | I²S speaker emitted both documented frequency bands |
| touch | PASS | two touchscreen positions delivered through FT6336 and released |
| touchsensor | PASS | SI12T click and forward swipe rendered, with idle control |
| wakeup | PASS | display sleeps and resumes once following RTC power wake |
| wav | PASS | SD WAV decoded and played at both fixture frequencies |
| quickstart-rgb | PASS | PY32 RGB565 LED refresh observed across the twelve pixels |
| stock | PASS | stock UIFlow2 home visible after input and USB CDC REPL round-tripped |

## Regressions

- CoreS3 15/15 PASS.
- Cardputer-ADV 11/11 PASS.
- Workspace execution reported 1985 passed and 0 failed tests across 151 result groups.
- native Clippy PASS.
- wasm Clippy PASS.

The first workspace run lacked pinned P4 and hosted firmware assets. The recovery used the repository's SHA-256-checked P4 and MicroPython fetch scripts. The baseline and candidate also gave the same P4 co-processor diagnostic. The test-only follow-ups update that expected message, two P4 SMP instruction counts and four SDIO diagnostic lines. All six golden comparisons produced identical baseline and candidate console, protocol reports and instruction counts.

Build the exact emulator with `CARGO_PROFILE_RELEASE_LTO=off CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8 CARGO_PROFILE_RELEASE_DEBUG=0 cargo build --release -p esp32sim --bin esp32sim`. The case runner and inputs are described in the parent record.

The [structured replay](run.json) binds each pass or documentation defect to its firmware, board profile, guest script and artifact hashes. Physical hardware and RF behavior were NOT RUN.

The [regression evidence](regression-evidence.summary.json) includes the six P4 comparisons, four instruction-count sentinels and two CAP SPI tag lengths.

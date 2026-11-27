# Validation and replay

The batch started at fork commit 3e90d09bd31b5658d8dd2b6fc5d820da5f293489. The pinned Arduino product documentation was built using m5stack:esp32@3.2.5. The StopWatch examples used the provisional CoreS3 OPI board profile from the source inventory.

The first StickS3 battery run stayed blank because the package strap selected another M5GFX probe. The StopWatch stripe was reproduced with the older QSPI framing before enforcing the panel chip-select boundary. Their later battery captures were compared to the published M5Stack example photos.
All results below are native virtual-device validation. The exact firmware and simulator SHA-256 values appear in the case summary. Stock StickS3 and StopWatch used the official v2.5.5 catalog images after the recorded v2.5.3 downloads returned HTTP 404.

## Reproduction

Run the listed checker on a compatible merged image tree with the native ESP32-S3 mask ROM. The original Cardputer SD example additionally uses the pinned FAT32 fixture containing the 12-second alternating-tone WAV.

```sh
CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=8 cargo build --release --bin esp32sim
ESP32SIM_ROM_DIR="$ROM_DIR" S3B_FIRMWARE_DIR="$FIRMWARE_DIR" S3B_STOCK_IMAGE="$STOCK_IMAGE" bash tools/run-s3b-docs.sh BOARD target/release/esp32sim OUT
tools/fetch-p4-firmware.sh && tools/fetch-micropython.sh
ESP32SIM_ROM_DIR="$ROM_DIR" cargo test --release --workspace --no-fail-fast -- --include-ignored --skip external_
```

Six P4 golden mismatches were independently replayed with the untouched starting commit. Both SMP instruction counts matched the candidate. The four hosted tests printed the same SDIO pin array that differed from the stored report format. The workspace result retains those failures.
The CoreS3 and Cardputer-ADV archived regression input revision was `829cfe6bc14cbdff40b1f4980a5e1ea4f130f66c`. The native counts were 15/15 and 11/11, respectively. The workspace log included 1976 passing tests and 6 failed tests.

## Shared model changes

- The original Cardputer uses its GPIO selector and key columns. Its SPI LCD and SD transport reuse the Cardputer-ADV path. The two boards retain their own input and audio wiring.
- Dial adds the GC9A01 binding, quadrature, PCF8563 latch, I2C reader and a virtual MIFARE tag, and the one-bit audio output.
- StickS3 adds its S3-PICO package identity, digital rail gates and GPIO-matrix RMT input. Both received input packets also completed the raw echo path as active-low transmitted symbols.
- StopWatch uses chip-select-framed CO5300 QSPI, the shared RX8130 calendar moved from Tab5, and register-backed PM1 and IOE1 power, motion and vibration.
- Other ESP32-S3 batches may reuse the PM1 and IOE1 register models, BMI270 motion and the S3 RMT RX path. The revision-W expander value is scoped to StopWatch.

## Individual results

### cardputer

| Case | Verdict | Evidence |
| --- | --- | --- |
| [battery](https://docs.m5stack.com/en/arduino/m5cardputer/battery) | PASS | idle and both sensor inputs produced distinct states |
| [button](https://docs.m5stack.com/en/arduino/m5cardputer/button) | PASS | guest reports press/release or both buttons |
| [display](https://docs.m5stack.com/en/arduino/m5cardputer/display) | PASS | display contains multicolor drawing and changes over time |
| [ir_nec](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec) | PASS | GPIO44 emits changing commands addressed to 0x1111 |
| [keyboard](https://docs.m5stack.com/en/arduino/m5cardputer/keyboard) | PASS | guest UI changes after physical matrix or quadrature inputs |
| [mic](https://docs.m5stack.com/en/arduino/m5cardputer/mic) | PASS | two rendered capture signals differ from silence and 733 Hz reaches speaker |
| [quickstart-display](https://docs.m5stack.com/en/arduino/m5cardputer/program) | PASS | display contains multicolor drawing and changes over time |
| [sdcard](https://docs.m5stack.com/en/arduino/m5cardputer/sdcard) | PASS | SPI read and write verified by serial, sector counters and persisted FAT32 bytes |
| [speaker](https://docs.m5stack.com/en/arduino/m5cardputer/speaker) | PASS | I2S output contains 7000 Hz and 4000 Hz tones |
| [speaker-sd-wav](https://docs.m5stack.com/en/arduino/m5cardputer/speaker) | PASS | all 12 one-second 440/660 Hz intervals agree across SPI SD and I2S |
| UIFlow2 2.5.4 | PASS | home frame, input-driven state change, and USB REPL arithmetic result |

### dial

| Case | Verdict | Evidence |
| --- | --- | --- |
| [button](https://docs.m5stack.com/en/arduino/m5dial/button) | PASS | guest reports press/release or both buttons |
| [buzzer](https://docs.m5stack.com/en/arduino/m5dial/buzzer) | PASS | GPIO3 PDM output contains 10000 Hz and 4000 Hz tones |
| [display](https://docs.m5stack.com/en/arduino/m5dial/display) | PASS | display contains multicolor drawing and changes over time |
| [encoder](https://docs.m5stack.com/en/arduino/m5dial/encoder) | PASS | guest UI changes after physical matrix or quadrature inputs |
| [quickstart-display](https://docs.m5stack.com/en/arduino/m5dial/program) | PASS | display contains multicolor drawing and changes over time |
| [rfid-1](https://docs.m5stack.com/en/arduino/m5dial/rfid) | PASS | separate virtual UIDs read through I2C FIFO and no UID without a tag |
| [rfid-2](https://docs.m5stack.com/en/arduino/m5dial/rfid) | PASS | separate virtual UIDs read through I2C FIFO and no UID without a tag |
| [rtc](https://docs.m5stack.com/en/arduino/m5dial/rtc) | PASS | RTC calendar advances in the guest |
| [touch](https://docs.m5stack.com/en/arduino/m5dial/touch) | PASS | idle and both sensor inputs produced distinct states |
| [wakeup](https://docs.m5stack.com/en/arduino/m5dial/wakeup) | PASS | button-triggered sleep followed by timer wake and guest reset |
| UIFlow2 2.5.3 | PASS | home frame and USB REPL arithmetic, with the rotary button read by the stock guest |

### sticks3

| Case | Verdict | Evidence |
| --- | --- | --- |
| [battery](https://docs.m5stack.com/en/arduino/m5sticks3/battery) | PASS | idle and both sensor inputs produced distinct states |
| [button](https://docs.m5stack.com/en/arduino/m5sticks3/button) | PASS | idle and both sensor inputs produced distinct states |
| [display](https://docs.m5stack.com/en/arduino/m5sticks3/display) | PASS | display contains multicolor drawing and changes over time |
| [imu](https://docs.m5stack.com/en/arduino/m5sticks3/imu) | PASS | idle and both sensor inputs produced distinct states |
| [ir_nec-1](https://docs.m5stack.com/en/arduino/m5sticks3/ir_nec) | PASS | guest serial and RMT46 GPIO data show NEC transmission |
| [ir_nec-2](https://docs.m5stack.com/en/arduino/m5sticks3/ir_nec) | PASS | both guest NEC payloads match the input address and command |
| [ir_nec-3](https://docs.m5stack.com/en/arduino/m5sticks3/ir_nec) | PASS | both payloads received and echoed as active-low RMT symbols on GPIO46 |
| [m5pm1-1](https://docs.m5stack.com/en/arduino/m5sticks3/m5pm1) | DOCS-DEFECT | m5pm1_1.ino:16 assigns Wire/I2C0 to the internal bus while M5.update at line 37 uses the M5Unified I2C1 route. Guest NACKs after successful PM1 initialization. A pin-route trace of the timer example found I2C0 disconnected from those GPIOs. |
| [m5pm1-2](https://docs.m5stack.com/en/arduino/m5sticks3/m5pm1) | DOCS-DEFECT | m5pm1_2.ino:18 assigns Wire/I2C0 to the internal bus while M5.update at line 52 uses the M5Unified I2C1 route. Guest NACKs after successful PM1 initialization. A pin-route trace of the timer example found I2C0 disconnected from those GPIOs. |
| [m5pm1-3](https://docs.m5stack.com/en/arduino/m5sticks3/m5pm1) | DOCS-DEFECT | m5pm1_3.ino:19 assigns Wire/I2C0 to the internal bus while M5.update at line 72 uses the M5Unified I2C1 route. Guest NACKs after successful PM1 initialization. A pin-route trace of the timer example found I2C0 disconnected from those GPIOs. |
| [mic](https://docs.m5stack.com/en/arduino/m5sticks3/mic) | PASS | 733 Hz and 997 Hz both reach the speaker and the silent control stays quiet |
| [quickstart-scrollgraph](https://docs.m5stack.com/en/arduino/m5sticks3/program) | PASS | display contains multicolor drawing and changes over time |
| [speaker](https://docs.m5stack.com/en/arduino/m5sticks3/speaker) | PASS | I2S output contains 7000 Hz and 4000 Hz tones |
| [wakeup-1](https://docs.m5stack.com/en/arduino/m5sticks3/wakeup) | FAIL | Pinned sketch writes PM1 shutdown then remains off through 17 virtual seconds. The register trace shows no PM1 timer arm. |
| [wakeup-2](https://docs.m5stack.com/en/arduino/m5sticks3/wakeup) | DOCS-DEFECT | wakeup_2.ino:16 assigns Wire/I2C0 to the internal bus while M5.update at line 36 uses the M5Unified I2C1 route. Guest NACKs after successful PM1 initialization. A pin-route trace of the timer example found I2C0 disconnected from those GPIOs. |
| UIFlow2 2.5.5 | PASS | home frame, input-driven state change, and USB REPL arithmetic result |

### stopwatch

| Case | Verdict | Evidence |
| --- | --- | --- |
| [battery](https://docs.m5stack.com/en/arduino/stopwatch/battery) | PASS | idle and both sensor inputs produced distinct states |
| [button](https://docs.m5stack.com/en/arduino/stopwatch/button) | PASS | guest reports press/release or both buttons |
| [display](https://docs.m5stack.com/en/arduino/stopwatch/display) | PASS | display contains multicolor drawing and changes over time |
| [imu](https://docs.m5stack.com/en/arduino/stopwatch/imu) | PASS | idle and both sensor inputs produced distinct states |
| [m5pm1_m5ioe1-1](https://docs.m5stack.com/en/arduino/stopwatch/m5pm1_m5ioe1) | PASS | PM1 timer powers the SoC back on and resets the guest |
| [m5pm1_m5ioe1-2](https://docs.m5stack.com/en/arduino/stopwatch/m5pm1_m5ioe1) | PASS | motion input wakes the guest after standby |
| [m5pm1_m5ioe1-3](https://docs.m5stack.com/en/arduino/stopwatch/m5pm1_m5ioe1) | PASS | guest observes PM1 IRQ |
| [m5pm1_m5ioe1-4](https://docs.m5stack.com/en/arduino/stopwatch/m5pm1_m5ioe1) | PASS | RTC IRQ wakes the guest after standby |
| [m5pm1_m5ioe1-5](https://docs.m5stack.com/en/arduino/stopwatch/m5pm1_m5ioe1) | PASS | guest observes PM1 IRQ |
| [m5pm1_m5ioe1-6](https://docs.m5stack.com/en/arduino/stopwatch/m5pm1_m5ioe1) | DOCS-DEFECT | m5pm1_m5ioe1_6.ino:107–113 starts the speaker after disabling the audio rail. Its enable callback repowers the rail, and the capture contains the 10 kHz tone described as silent. Connector selects and programmed motor duty passed. |
| [mic](https://docs.m5stack.com/en/arduino/stopwatch/mic) | PASS | 733 Hz and 997 Hz both reach the speaker and the silent control stays quiet |
| [quickstart-bargraph](https://docs.m5stack.com/en/arduino/stopwatch/program) | PASS | display contains multicolor drawing and changes over time |
| [rtc-1](https://docs.m5stack.com/en/arduino/stopwatch/rtc) | PASS | RTC calendar advances in the guest |
| [rtc-2](https://docs.m5stack.com/en/arduino/stopwatch/rtc) | PASS | RTC calendar advances in the guest |
| [speaker](https://docs.m5stack.com/en/arduino/stopwatch/speaker) | PASS | I2S output contains 10000 Hz and 4000 Hz tones |
| [touch-1](https://docs.m5stack.com/en/arduino/stopwatch/touch) | PASS | idle and both sensor inputs produced distinct states |
| [touch-2](https://docs.m5stack.com/en/arduino/stopwatch/touch) | PASS | both touch targets inside the button display Pressed, with idle and outside controls Released |
| [vibration](https://docs.m5stack.com/en/arduino/stopwatch/vibration) | PASS | all nine vibrator PWM1 duties observed |
| UIFlow2 2.5.5 | PASS | home frame, input-driven state change, and USB REPL arithmetic result |

## Limits

The Dial stock guest read idle, pressed and released levels from the rotary button while connected over USB. Its offline menu frame stayed unchanged during the control sequence.

StickS3 reports over the GPIO13 interrupt path. The four Wire-based sketches reassign the same port pins to I2C0 after M5Unified initializes I2C1. The Stock UIFlow2 path used the normal shared-board transport.
Stock StickS3 was used for a separate power diagnostic through USB CDC and its on-chip I2C1. The guest read the PM1 ID, programmed a four-second wake, and issued shutdown after the pending USB reply had cleared. The PM1 wake counter incremented and the guest rebooted at 12.403 s. A separate power-key control restarted the pinned wake example when the virtual switch was pressed at 6.000 s. Neither control changes the documented sketches’ verdicts.
The StopWatch relay and amplifier wiring follow the C152 main board schematic. [StopWatch schematic, sheet 4](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1242/C152-SCH_Stopwatch_PRJ_Main_VA_20251201_2026_04_24_17_46_22.pdf)
The StopWatch connector test checked the expander register and the mux selection state. The separate J6 external connector had no attached virtual USB cable or serial accessory in the fixture.

The comparative execution sentinel uses release binaries built with differing link settings. Instruction counts and console equality are the portable observations. The sample CPU measurements do not establish a throughput change.

Evidence captures and any per-device USB descriptors are kept out of this record. Only image hashes and reviewed result summaries are included.

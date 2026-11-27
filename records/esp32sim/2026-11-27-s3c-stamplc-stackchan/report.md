# StamPLC and StackChan on esp32sim

Implemented the two ESP32-S3 boards for the pinned official Arduino documentation and M5Burner UIFlow2 2.5.3 images.
The path is native esp32sim virtual-device validation on macOS arm64. Firmware images, scripts, frames and protocol receipts are identified by SHA-256 in [run.json](run.json).

Source commit `f86f05093398748d7bf84bb7c396d7182e3cd2e4`. The first complete board runs used `08ea5102adc190df5dffaf7e231977cdc651c228c3b8b8026355fcc6f627cafd`. The follow-up binary SHA-256 is `a55f16919e630a861caafd17c0a24a75abb161e581a6d5a7b3fd728a5b081fcf`.

StamPLC routes its buttons, relay outputs, and isolated inputs through the I²C expanders. Its sensors and clock use INA226, LM75B and RX8130. Display detection and SPI storage share modeled pins. Modbus uses the guest-selected S3 UART route, and CAN uses the S3 TWAI data path.

StackChan extends CoreS3 with PY32 LED output, SI12T head gestures, INA226, and an I²C ST25R3916. The addressed SCSCL servos receive UART1 frames from the guest and expose their simulated encoder angles. The fixture observed motor settling as well as commanded positions.

## Guest cases

| Case | Result | Observation |
| --- | --- | --- |
| stamplc/button | PASS | guest rendered all three button labels compared with the untouched screen |
| stamplc/buzzer | PASS | GPIO44 LEDC produced 523, 659 and 880 Hz tones at 50 ms |
| stamplc/can | PASS | TWAI TX and extended-ID peer reply with eight matching payload bytes |
| stamplc/display | DOCS-DEFECT | Pinned display.md line 7 snippet calls Display as a field |
| stamplc/input_output-1 | PASS | guest toggled all four modeled relay outputs |
| stamplc/input_output-2 | PASS | zero-input control and two mapped AW9523 input patterns |
| stamplc/modbus-1 | PASS | three Modbus master writes echoed over UART with mapped relay changes |
| stamplc/modbus-2 | PASS | guest slave-peer exchange on RS485 including coils and input registers |
| stamplc/rgb_led | PASS | all five requested GPIO-expander RGB states |
| stamplc/rtc | PASS | guest set RX8130 calendar and read advancing time |
| stamplc/sd_card | PASS | SPI SD guest writes and reads test.txt, with no-media control |
| stamplc/sensor | PASS | three distinct LM75B and INA226 readings via guest I2C |
| stamplc/quickstart-display | PASS | multicolor drawing over ST7789 SPI within the 240×135 crop |
| stamplc/stock | PASS | stock UIFlow2 home visible after input and USB CDC REPL round-tripped |
| stackchan/battery | PASS | two injected INA226 voltage and load readings on LCD |
| stackchan/button | PASS | AXP2101 PMIC key produces rendered Btn PWR |
| stackchan/camera | PASS | two distinct camera frames with VSYNC and zero dropped data |
| stackchan/display | PASS | guest-drawn multicolor circles and rectangles |
| stackchan/imu | PASS | two distinct BMI270 accelerometer and gyro readings on LCD |
| stackchan/ir_nec | PASS | GPIO carrier delivered two valid NEC frames |
| stackchan/ltr553 | PASS | two distinct LTR553 ranges and a no-stimulus control |
| stackchan/mic | PASS | I²S mic recording played back distinct 733 Hz and 548 Hz signals, with silence control |
| stackchan/nfc-1 | PASS | guest identifies and reactivates two Type 2 tags, with a no-tag control |
| stackchan/nfc-2 | NOT RUN | sketch awaits BtnA, outside the modeled FT6336 touch range |
| stackchan/nfc-3 | NOT RUN | guest booted, virtual reader and passive-target exchange unavailable |
| stackchan/nfc-4 | NOT RUN | guest booted, authenticated MIFARE Classic read/write unavailable |
| stackchan/nfc-5 | NOT RUN | guest booted, writable NDEF tag unavailable |
| stackchan/nfc-6 | NOT RUN | guest booted, authenticated MIFARE Classic value blocks unavailable |
| stackchan/pic | PASS | file reads are visible in the framebuffer and use SPI SD |
| stackchan/rgb | PASS | PY32 RGB565 LED refresh observed across the twelve pixels |
| stackchan/rtc | PASS | guest associates with virtual AP, consumes NTP and draws clock |
| stackchan/sdcard | PASS | file reads are visible in the framebuffer and use SPI SD |
| stackchan/servo-1 | PASS | touch saves two SCSCL encoder positions and restores them after displacement |
| stackchan/servo-2 | PASS | top touch drives 45° pitch and then 90° yaw using serial servos |
| stackchan/speaker | PASS | I²S speaker emitted both documented frequency bands |
| stackchan/touch | PASS | two touchscreen positions delivered through FT6336 and released |
| stackchan/touchsensor | PASS | SI12T click and forward swipe rendered, with idle control |
| stackchan/wakeup | PASS | display sleeps and resumes once following RTC power wake |
| stackchan/wav | PASS | SD WAV decoded and played at both fixture frequencies |
| stackchan/quickstart-rgb | PASS | PY32 RGB565 LED refresh observed across the twelve pixels |
| stackchan/stock | PASS | stock UIFlow2 home visible after input and USB CDC REPL round-tripped |

## Regressions

- CoreS3 base 15/15 PASS.
- Cardputer-ADV base 11/11 PASS.
- CoreS3 first 15/15 PASS.
- Cardputer-ADV first 11/11 PASS.
- CoreS3 final 15/15 PASS.
- Cardputer-ADV final NOT RUN.
- native Clippy PASS.
- wasm Clippy PASS.

The instruction-count sentinels ran three paired native releases for three seconds of guest time per trial. Review the individual CPU timings on the shared host in [instruction counts](evidence/instruction-counts.summary.json).

## Reproduction and limits

Build the named source with `cargo build --release -p esp32sim --bin esp32sim`. Set `ESP32SIM_ROM_DIR` to the S3 ROM directory and run `python3 tools/run-s3c-docs.py --help`. Supply the pinned documentation firmware, inventory, ROM and fixtures. The runner copies the input binary and hashes it in each board receipt.

The first StamPLC boot failed its LCD probe. Correcting the software SPI order allowed the guest to draw. The first Modbus slave run asserted when TX_DONE stayed set during RS485 teardown. A later console capture identified UART1 for the slave and UART2 for the client. The board routes the active UART's RTS to the transceiver. The first StackChan NFC pass through anticollision showed a one-byte SAK where the driver's FIFO read required the two trailing CRC bytes. The correction exposes all three bytes.

Stock checks exercise the UIFlow2 home screen and USB-OTG CDC REPL. The first StackChan boot requires a long touch for calibration. Physical hardware, electrical behavior and RF performance were NOT RUN. The coordinator can omit the batch branch from the integration plan to roll back the board additions.

The CAP SPI regression used the compatibility prelude with stock UIFlow2 and each of two tag lengths. Both displayed a card type and recorded 33 selections. The [observed markers](evidence/validated-markers.summary.json) contain the measured frame and script hashes without tag identifiers.

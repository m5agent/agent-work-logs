# CoreS3 display and serial audit

## Arduino console

Arduino-ESP32 3.2.5 compiled the fixtures with `ARDUINO_USB_MODE=1`, `ARDUINO_USB_CDC_ON_BOOT=1`, and `CORE_DEBUG_LEVEL=0`. `HardwareSerial.h:411–413` maps `Serial` to `HWCDCSerial`. `main.cpp:91–93` automatically calls `Serial.begin()` only for USB-OTG CDC. The debug report in `chip-debug-report.cpp:292–300` can start HWCDC, but `main.cpp:43–58` gates it on debug level or a weak hook returning false. The IMU ELF calls that hook and its `app_main` goes directly to `initArduino()`. The HWCDC constructor at `HWCDC.cpp:255–261` only registers deinit callbacks. `begin():303–318` allocates the TX mutex and ring buffer. `write():418–425` returns zero when they are absent before polling connection state. M5Unified 0.3.0 defaults `serial_baudrate` to zero at `M5Unified.hpp:94–95`, and the guarded call is at `M5Unified.inl:2077–2080`.

The IMU guest's USB-Serial/JTAG MMIO observations show ROM `EP1` writes and periodic `INT_RAW/CLR` SOF polling. There were no writes to `INT_ENA`. The ESP32-S3 SDK headers packaged with Arduino 3.2.5 are from `idf-release_v5.4-858a988d-v1`. In `soc/esp32s3/register/soc/usb_serial_jtag_reg.h`, EP1/EP1_CONF are offsets `0x00`/`0x04`, INT_ENA is `0x10`, and SOF and SERIAL_IN_EMPTY are bits 1 and 3. ROM and `ets_printf` logging use console hooks that are independent of `Serial.printf`. The original `wav.ino:18` initializes HWCDC and completes playback with `--console usb`, exercising the data path with the original binary. The UART/HWCDC model requires no change for these sketches.

## Display and related devices

The CoreS3 glass is mounted landscape in the chassis, above the camera. M5GFX 0.3.0 changed the rotation offset from 3 to 0, with the former `setRotation(1)` now equivalent to `setRotation(0)`. In the pinned source, `M5GFX.cpp:1166–1172` sets the offset to zero, `Panel_LCD.inl:131–169` swaps logical dimensions for odd rotations and emits MADCTL, and `Panel_LCD.hpp:85–96` supplies MX/MV/MH for rotation 1. The speaker and mic sketches explicitly request rotation 1 and produce `0x6c`; rotation 0 uses `0x08`. On a fixed 320×240 glass, MV exchanges the input axes, MX reverses the resulting column, and MH controls refresh direction. Guest text advancing on logical x therefore advances along physical y. The older CoreS3 mic photo and the checked QEMU speaker artifact show horizontal text. The pinned firmware's explicit rotation and the fixed-glass transform explain the esp32sim result. Applying `(x, y) → (319 − y, x)` to the QEMU capture maps its 1003 green text pixels exactly onto the esp32sim mask. [ILI9342C v1.00 §8.2.29](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/core/ILI9342C-ILITEK.pdf), [M5GFX 0.3.0 rotation notes](https://github.com/m5stack/M5GFX/releases/tag/0.3.0), [CoreS3 chassis and LCD](https://docs.m5stack.com/en/core/CoreS3)

The audit found a separate pixel-write defect. MX/MY previously clamped out-of-range coordinates into the edge pixel. The new unit regression uses MX, MY and MV together and observed four writes on base versus one valid write after the fix. The model now bounds-checks physical coordinates before mirroring. [ILI9342C v1.00 §§8.2.20–21](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/core/ILI9342C-ILITEK.pdf)

The power sketch shows connected VBUS of 5000 mV and disconnected VBUS of 0 mV. M5Unified 0.3.0 checks PMIC status bit 5 before reading the VBUS ADC (`AXP2101_Class.inl:211–214,252–259`). The two camera inputs produced pixel-exact h-mirrored RGB565 panels after LCD_CAM/GDMA capture. The camera ELF embeds the `0x14=0x11` GC0308 register initializer, enabling mirror bit 0. The mic test uses an injected 733 Hz tone and the sketch's touch-click playback path at `mic.ino:95–119`. The physical power key selects noise-filter level at `mic.ino:82–91`. Microphone RMS in this report is expressed in digital PCM counts.

## Reproduction

Use the unchanged merged firmware and mask ROM identified in [run.json](run.json). The simulator runs with `--board m5stack-cores3 --boot rom`. Set `CORES3_FIRMWARE_DIR` to the prebuilt CoreS3 images, `CORES3_RTC_WIFI` to the simulated AP parameters matching the RTC sketch, and `CORES3_FIXTURES` to the runner fixture root. The RTC test seeds the virtual network clock at epoch 1764000000. Each capture is a fresh run using the runner's checked-in inputs and a copy of the runtime binary.

```sh
tools/run-cores3-docs.sh "$bin" "$new_outdir"
python3 tools/check_cores3.py "$new_outdir"
```

For UIFlow2 v2.5.3, use a 16 MiB Flash / 8 MiB PSRAM configuration. Capture home and touch at 8 emulated seconds. The touch action presses (34, 47) at 4.0 seconds and releases at 4.3. The 30-second USB-OTG run attaches and enumerates a CDC host, interrupts the firmware after startup, and issues `print(1+1)` and `import M5; M5.Lcd.fillScreen(0xFF0000)`. Verify the REPL result and all-red 320×240 panel.

The checker fails closed on missing evidence. Negative controls replaced a touch frame, microphone WAV, SD image, USB console and camera report independently. Each substitution failed its case. The checked-in harness is tied to the pinned fonts, firmware and deterministic fixtures. Hardware validation was `NOT RUN`. The runner operates without Device Service ports.

## Regression results

The 560 requested library tests and the ESP32-S3 integration tests passed. The full release workspace suite passed 1948 tests, including all 48 CLI goldens, with 34 external cases filtered. Native and wasm32 Clippy completed with `-D warnings`. Cargo emitted one advisory for the existing wasm manifest dependency when the target is native.

| A/B workload | Guest instructions per core | Baseline median user seconds | Candidate median user seconds |
| --- | --- | ---: | ---: |
| hello (30 s) | 11,934,783 + 6,775,776 | 0.43 | 0.42 |
| c3-hello (30 s) | 4,800,000,000 | 4.64 | 4.73 |
| c6-hello (30 s) | 4,800,000,000 | 2.80 | 2.85 |
| pocket-tank (4 s) | 541,260,912 + 837,395,629 | 9.56 | 9.75 |

Instruction counts and console SHA-256 matched across all three alternating pairs in each workload. The timing samples came from a busy host and serve as an environment-specific comparison. The model-backed 30-second Pocket Tank attempt was stopped for runtime cost and replaced by the four-second run above.

An initial repeat was interrupted when the runner was revised while Bash was still reading it. The restarted suite took a local binary copy and matched the first completed run's verdicts and all 37 PNG, WAV and SD image files byte-for-byte. The pinned execution is the one identified in the receipt.

## Rollback

Revert the DCS bounds-check commit to restore the prior mirror handling. The diagnostics harness and Clippy test changes are separate commits.

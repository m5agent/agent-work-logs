# PaperDIY EPD sleep/wakeup probe (ESP-IDF)

Minimal M5GFX application used for the M5GFX #447 virtual-device A/B run.

## Layout

- `CMakeLists.txt` – project; expects the M5GFX source tree at `components/M5GFX`
  (a directory or symlink named exactly `M5GFX`).
- `main/main.cpp` – prints `board`, `display_oe`, draws a page, sleeps, wakes, draws again,
  printing `DRAW1_DONE / SLEEP_DONE / WAKE_DONE / DRAW2_DONE`.
- `sdkconfig.defaults` – ESP32-S3, 16 MiB flash, octal PSRAM at 80 MHz (PaperDIY).

## Build

```bash
git clone https://github.com/m5stack/M5GFX.git <work>/M5GFX
git -C <work>/M5GFX checkout <M5GFX commit>
ln -s <work>/M5GFX components/M5GFX
. $IDF_PATH/export.sh
idf.py set-target esp32s3
idf.py build
python -m esptool --chip esp32s3 merge-bin -o paperdiy.bin \
  --flash-mode dio --flash-size 16MB \
  0x0 build/bootloader/bootloader.bin \
  0x8000 build/partition_table/partition-table.bin \
  0x10000 build/<project>.bin
```

Run `paperdiy.bin` on a PaperDIY Device-Service session (`device_id=paperdiy`, `runtime=qemu`)
and wait for `PR447 DRAW2_DONE`.

Builds used for the record: base `72001da0fdd7232a8a8ac77cd84120801f879496`,
PR head `a5fdf82cae2ebf3385f622302a1ffe917b197fdc`, both on ESP-IDF v6.1.

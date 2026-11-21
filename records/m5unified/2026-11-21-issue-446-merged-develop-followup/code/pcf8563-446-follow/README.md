# PCF8563 follow-up probe (M5Dial / ESP32-S3 virtual device)

Minimal ESP-IDF application used to re-check m5stack/M5Unified#446 on the merged
develop commit (`dae3b5d`, merge of #447), using the same `PCF8563_Class` driver
path on the `dial` virtual device (M5Dial / QEMU / PCF8563 register model).

It pre-arms the PCF8563 with `0x01=0x01`, `0x0F=2`, `0x0E=0x82`, then checks:

1. `0x0E` after `M5.begin(cfg)` with `cfg.disable_rtc_irq = false`
2. `0x0E` after `M5.Rtc.clearIRQ()`
3. `0x0E` after another `M5.Rtc.begin(&M5.In_I2C)`
4. `0x0E` after `M5.Rtc.setTimerIRQ(0)`
5. `0x0E` after `setTimerIRQ(3000)` + `disableIRQ()`
6. `begin()` + `disableIRQ()` (the default `disable_rtc_irq=true` pair)

## Build

```bash
export IDF_PATH=/path/to/esp-idf            # v6.0.2 used in the record
export IDF_COMPONENT_MANAGER=0
export M5GFX_PATH=/path/to/M5GFX            # 28d4794
idf.py set-target esp32s3
idf.py build
idf.py merge-bin
```

`CMakeLists.txt` expects M5Unified at `../../M5Unified` relative to this project
(or adjust `_root`); M5GFX comes from `M5GFX_PATH`. If M5Unified sits next to an
`M5GFX` checkout, keep that sibling available: M5Unified's CMakeLists selects the
component name `M5GFX` only when `../M5GFX/CMakeLists.txt` exists, otherwise it
requires the lower-case `m5gfx` managed component.

## Run

```bash
python3 run_on_device_service.py --image build/merged-binary.bin --out run
```

Requires a reachable Device Service API (`DEVICE_SERVICE_API`, base ending in
`/api/v1`) with the `dial` profile. The completion marker is
`PCF8563_446_FOLLOW_DONE` in the serial capture. The QEMU PCF8563 model has no
countdown/TF logic, so `0x0F` does not decrement; that is a model limit, not
evidence that the timer is stopped.

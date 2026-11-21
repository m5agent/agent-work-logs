# PCF8563 Timer_control probe (M5Dial / ESP32-S3 virtual device)

Minimal ESP-IDF application used to compare M5Unified PR #447 (`4a0ebfd`) against
develop (`11bfd4b`) on the same PCF8563 driver path.

It pre-arms the PCF8563 before `M5.begin()`, then checks:

1. `Timer_control (0x0E)` after `M5.begin(cfg)` with `cfg.disable_rtc_irq = false`
2. a second `M5.Rtc.begin(&M5.In_I2C)`
3. `M5.Rtc.setTimerIRQ(3000)` and another `begin()`
4. `M5.Rtc.disableIRQ()`
5. a stopped timer (`0x0E = 0x00`) through `begin()`
6. the default path (`begin()` + `disableIRQ()`)
7. `M5.Rtc.setTimerIRQ(0)`
8. a running timer with `TD = 1/60 Hz` (`0x0E = 0x83`) through `begin()`

## Build

```bash
export IDF_PATH=/path/to/esp-idf            # v6.0.2 used in the record
export IDF_COMPONENT_MANAGER=0
export M5GFX_PATH=/path/to/M5GFX            # 28d4794
idf.py set-target esp32s3
idf.py build
idf.py merge-bin
```

The CMakeLists expects M5Unified at `../../M5Unified` relative to this project
(or adjust `_root`); M5GFX comes from `M5GFX_PATH`.

## Run

```bash
python3 run_on_device_service.py --image build/merged-binary.bin --out run
```

Requires a reachable Device Service API (`DEVICE_SERVICE_API`, base ending in
`/api/v1`) with the `dial` profile.

Expected markers are documented in `evidence/register-readback.txt`. Note that
the QEMU PCF8563 model has no countdown/TF logic, so `TF_AFTER_*` staying at -1
is a model limit, not evidence that the timer is stopped.

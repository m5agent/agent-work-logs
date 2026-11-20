# PCF8563 Timer_control reproducer (M5Dial / ESP32-S3 virtual device)

This is the minimal ESP-IDF application used for the register-level reproduction.
It links M5Unified 0.3.0 (commit `96576a1`) and M5GFX 0.3.0 (commit `28d4794`) as
local components.

Build (with an ESP-IDF v6.0.2 shell and M5GFX checked out next to M5Unified):

```bash
export M5GFX_PATH=/path/to/M5GFX
idf.py set-target esp32s3
idf.py build
idf.py merge-bin
```

Run on a Device Service instance that has the `dial` profile:

```bash
export DEVICE_SERVICE_API=http://<service>/api/v1
python3 run_on_device_service.py --image build/merged-binary.bin --out run
```

Expected markers in the serial log:

- unmodified library: `POST_BEGIN ... TC=0x03`, `AFTER_REBEGIN ... TC=0x03`
- patched library: `POST_BEGIN ... TC=0x82`, `AFTER_REBEGIN ... TC=0x82`

The application deliberately initializes the internal I2C bus and arms the RTC
timer before `M5.begin()` so that the startup path starts from a timer that is
already enabled, mirroring an MCU reset with the PCF8563 still powered.

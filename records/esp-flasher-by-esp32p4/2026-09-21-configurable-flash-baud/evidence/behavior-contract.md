# Flash baud behavior contract

## Defaults

- ROM loader synchronization: 115200 baud.
- Image transfer default: 1500000 baud.
- Legacy fallback order: 1500000, 921600, 460800, 230400, 115200.
- Supported range: 9600 through 3000000 baud.

## API fields

High-level task:

```json
{
  "artifact_id": "fw-example",
  "firmware": {
    "address": 0,
    "reboot": true,
    "flash_baud": 1500000
  }
}
```

Target profile:

```json
{
  "target": {
    "flash_address": 0,
    "flash_baud": 1500000,
    "serial_baud": 115200
  }
}
```

Explicit plan:

```json
{
  "op": "flash",
  "args": {
    "url": "public artifact URL",
    "address": 0,
    "reboot": true,
    "baud": 1500000
  }
}
```

`serial_baud` remains the monitor/application UART rate and is not the DUT flash rate.

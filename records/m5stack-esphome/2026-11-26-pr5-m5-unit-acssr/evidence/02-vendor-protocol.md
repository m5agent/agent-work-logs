# Unit ACSSR / DCSSR protocol cross-check

Public sources:

- Vendor library: `m5stack/M5Unit-ACSSR@2996144a6d821f0274079cdb11607c650ad87195`
  <https://github.com/m5stack/M5Unit-ACSSR/blob/2996144a6d821f0274079cdb11607c650ad87195/src/M5_ACSSR.h>
  and `src/M5_ACSSR.cpp`.
- Unit internal firmware: `m5stack/M5Unit-ACSSR-Internal-FW@45e62980e62bd124fe75c6ed50d76ac05e64b9dc`
  <https://github.com/m5stack/M5Unit-ACSSR-Internal-FW/tree/45e62980e62bd124fe75c6ed50d76ac05e64b9dc>.

## Register map

| I2C address | Register | Access | Size | Meaning |
| --- | --- | --- | --- | --- |
| 0x50 | 0x00 | read/write | 1 byte | Relay level (`1` = on, `0` = off) |
| 0x50 | 0x10 | read/write | 3 bytes | RGB LED, R then G then B |
| 0x50 | 0x20 | write | 1 byte | Change the unit I2C address (not exposed by the ESPHome component) |
| 0x50 | 0xFE | read | 1 byte | Firmware version |

The vendor library selects a register with a write transaction and then reads in a
separate transaction (`M5_ACSSR::readBytes`), which is what the component's
`read_register_()` does. The component exposes the default 0x50 address through
`i2c_device_schema(0x50)`.

## Boot behavior

`main/acssr.c:133-154` (`initial_control()`): the unit flashes its LED, waits
`vTaskDelay(pdMS_TO_TICKS(3000))`, turns the LED off, drives the relay off
(`ctrl_set_op(0)`), and only afterwards calls `i2c_slave_init()`. The component's
10 x 1 s reconnect window is consistent with that 3 s window.

## Shadow-register semantics

`components/test/i2c_slave.c:75-96`: the I2C ISR stores every written byte except
the version register into `rw_register_data[]`, and a read returns that array.
So a read of 0x00/0x10 is the unit's write shadow, not a contact or optical
measurement. `reg_length` and the write offsets match the component's one-byte
relay and three-byte RGB transactions.

## What this check does not prove

- The shadow byte is not proof that the SSR contact is closed or that the LED
  actually emits the requested color.
- Button and Modbus/RS485 modes of the unit are not modeled or exercised.
- The 0x20 address-change register is not implemented in the component.

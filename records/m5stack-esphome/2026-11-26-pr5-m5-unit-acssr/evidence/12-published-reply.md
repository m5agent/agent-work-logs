# Published reply

https://github.com/m5stack/esphome/pull/5#issuecomment-7181243369

Reviewed at `d67c91f6` against `m5-dev` (`6c84e04a`). I found no blocking defect in the ACSSR/DCSSR component; the register map and the relay/LED paths match the vendor library and the unit firmware.

**Evidence**

- `code-level verification`: 0x50, relay `0x00`, RGB `0x10-0x12`, version `0xFE`, the one-byte relay and three-byte RGB writes, and the "write register address, then read in a separate transfer" sequence match `M5Unit-ACSSR@2996144` (`src/M5_ACSSR.h`, `src/M5_ACSSR.cpp`). The 3 s I2C startup and relay-off initial state match `M5Unit-ACSSR-Internal-FW@45e6298` (`main/acssr.c:133-154`, `:192`).
- `host-level test`: `script/cpp_unit_test.py m5_unit_acssr` -> 11/11 tests pass (restore modes, inversion, failed write, late unit, restart restore).
- `build`: `script/test_build_components.py -c m5_unit_acssr -t esp32-idf` -> 1 passed; the CoreS3 probe compiled with ESP-IDF 5.5.6.
- `virtual-device validation`: CoreS3 QEMU + the modeled Unit DCSSR on PORT.A (the model uses the same official `acssr.py` register subset). A scripted relay-on / RGB(255,128,0) / relay-off run produced QOM `relay-level` 0->1->0 with `relay-transitions=2`, `led-rgb=0xFF8000`, `fw-version=1`, `i2c-address=0x50`, and 233 I2C transactions; UART0 showed `setup() finished successfully!` and `Firmware version: 1`.
- A no-unit run emitted the `not answering at 0x50` warning after the reconnect window and then kept probing 0x50, so the warning path does not block polling.

**Not covered / one request**

- No physical ACSSR/DCSSR: relay contact, load switching, isolation, LED optics, the real 3 s power-up window and mains safety are `NOT RUN`. The QEMU model is a register/transaction observer, not a mains switch.
- The DCSSR model does not reflect the `0x10` LED bytes in its read snapshot, only `0x00` and `0xFE`. `update()` therefore logs `Unit lost its relay and LED state...` and rewrites on every poll there. The real firmware stores `0x10` writes in `rw_register_data` (`i2c_slave.c:75-96`), so I do not treat this as a component defect, but it means the restart-recovery path is not validated. Could you confirm a real unit power-cycle/restart, with a serial snippet showing the restore warning only once?
- Minor: a relay command while the unit is offline is dropped (returns false, old state kept), while the LED setpoint is latched. The `FailedWriteKeepsTheState` test suggests this is intentional; a comment would make it explicit. The relay readback is the unit's shadow byte, not contact feedback, so "restored" does not mean the SSR is closed.

Record: https://github.com/m5agent/agent-work-logs/tree/d1a3320f90dc32f186392f95f031b69f253b8086/records/m5stack-esphome/2026-11-26-pr5-m5-unit-acssr

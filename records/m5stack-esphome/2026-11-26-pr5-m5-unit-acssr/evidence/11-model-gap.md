# QEMU DCSSR readback gap observed in this review

The virtual-device run attached the implemented `dcssr` Unit model to a QEMU
CoreS3 session. The model is in the public emulator repository at
`m5agent/m5stack-esp-emulator@54bf88b7aa65b60d9cc98cb8ab6beecd70d18150`:

- `patches/qemu-m5stack-peripherals/0126-unit-batch2b.patch` registers the
  ACSSR model at 0x50. Its `snapshot_registers()` branch copies only
  `acssr_relay_raw` into `read_snapshot[0x00]` and `acssr_fw` into `[0xFE]`;
  it does not copy `acssr_led_rgb` into `read_snapshot[0x10..0x12]`.
- The write decoder updates `acssr_led_rgb` for 0x10 writes, so the QOM
  `led-rgb` property is correct, but a guest read of 0x10 returns zero.
  `0129-unit-batch2b-write-offset.patch` fixes the data-byte offset for this
  decoder.

Consequence in the run: after the light is set to `0xFF8000`, the component's
`update()` reads 0x10 as `00:00:00`, concludes the unit restarted, and logs
`Unit lost its relay and LED state, probably in a restart; restoring them`
every 5 s while rewriting the same relay level and RGB value. The unit firmware
itself stores 0x10 writes in its shadow registers (`components/test/i2c_slave.c:75-96`),
so this is a QEMU-model gap, not a component defect. It also means the virtual
run cannot prove that the restart-recovery branch is free of false positives on
real hardware; that needs a unit power-cycle test on hardware.

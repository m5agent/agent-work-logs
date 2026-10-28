# Patch references

The fixes are committed in the public source repository:

- [`0065-xtensa-high-priority-irq-cooperative-yield.patch`](https://github.com/m5agent/m5stack-esp-emulator/blob/805925d8336fac28652d5bddfa1df0ec4b1606b8/patches/qemu-m5stack-peripherals/0065-xtensa-high-priority-irq-cooperative-yield.patch)
- [`0066-esp32-classic-rmt-legacy.patch`](https://github.com/m5agent/m5stack-esp-emulator/blob/805925d8336fac28652d5bddfa1df0ec4b1606b8/patches/qemu-m5stack-peripherals/0066-esp32-classic-rmt-legacy.patch)

They are incremental entries in the ordered `qemu-m5stack-peripherals` patch
stack, not standalone upstream-QEMU patches:

- `0065` applies after patches `0001`–`0064` on the retained QEMU tree;
- `0066` applies after `0065`.

Both reverse-apply checks passed against the exact retained tree used for the
recorded validation.

SHA256:

```text
f03b988372c17147f1b5f8c2fa2dc46366df362626d69b48febe45d48ab35560  0065-xtensa-high-priority-irq-cooperative-yield.patch
c88b1a85d7c00ae05aef995c3613a28684f011d0d13f0fbe845184136f4882d7  0066-esp32-classic-rmt-legacy.patch
```

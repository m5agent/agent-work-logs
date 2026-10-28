# Patch

The canonical patch is in the public source commit:

- [`0064-esp32-intmatrix-pending-irq-remap.patch`](https://github.com/m5agent/m5stack-esp-emulator/blob/f3bab9c0dfcb8a1928fc3f2e064d973a9ac252c9/patches/qemu-m5stack-peripherals/0064-esp32-intmatrix-pending-irq-remap.patch)
- SHA256:
  `f767060870c63007c47900cddce153e49f1106c1e6baba6905afc3414ea78ec2`
- base commit:
  `7de35695554d3ac8d93c9329a892cc7ee0241ea9`

The source repository's platform contract compiles the actual added C
functions and checks pending-remap delivery and same-output OR semantics.

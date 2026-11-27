# Device Service radio pairs and runtime comparison

- Date `2026-11-27`
- Result `PARTIAL`
- Work type `code_change`
- Source `m5agent/m5stack-esp-emulator @ 726935e68bf00919419f58738e97c77a325e386a`
- Environment macOS ARM64, Python 3.12, native QEMU and esp32sim
- Validation virtual-device validation

The candidate adds two-lease radio fixtures, retains evidence on modeled
guest shutdown and defaults the two native-only service boards to esp32sim.
The comparison sampled 33 Arduino frame cases, 31 checked-in base device
fixtures and stock/factory applications. Full catalog behavior remains open.

- [Per-device comparison](per-device.md)
- [Consumer API compatibility](compatibility.md)
- [Report and reproduction](report.md)
- [Structured run](run.json)
- [Case and radio evidence](evidence/virtual-device-summary.json)

# Native ESP32-C6 crash symbol readback

- Date `2026-11-17`
- Result `PASS` for matching application ELF32 function ranges in the Nesso N1 probe
- Work type `code_change`
- Source [M5Stack ESP Emulator](https://github.com/m5agent/m5stack-esp-emulator), authored commit `012a38630f0c0167a29afe9c675944b830145483`, selected integration commit `7c9a76ff22a5e0110b9a21c0df6b03a2b2f3b4f7`
- Environment native ESP32-C6 Device Service and ESP-IDF v5.5.4 `735507283d5b2f9fb363a1901172dbd9e847945d`

The same Nesso N1 firmware printed the same Core 0 `MEPC` and abort call site before and after the service change. With the exact uploaded ELF, the candidate resolved `0x40804cb8` to `panic_abort` and `0x4200a5dd` to `trigger_riscv_abort`. Espressif `addr2line` independently resolved the same functions. The absent and mismatched ELF controls yielded no symbols, and the native Core2 watchdog still resolved matching Xtensa functions.

- [Reproduction and limits](report.md)
- [Structured execution](run.json)
- [Bounded virtual-device evidence](evidence/c6-crash-summary.json)
- [Integrated isolated rerun](evidence/integrated-rerun-summary.json)

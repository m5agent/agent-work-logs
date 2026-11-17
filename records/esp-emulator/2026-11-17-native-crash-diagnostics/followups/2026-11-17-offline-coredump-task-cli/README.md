# Core2 offline FreeRTOS task decoding

- Date `2026-11-17`
- Result `PASS` for offline analysis of the two retained Core2 virtual-device captures
- Work type `code_change`
- Source [M5Stack ESP Emulator](https://github.com/m5agent/m5stack-esp-emulator), commit `9436f1475dd03490c304cd90f5780bf5e6484b4e`
- Environment Core2 native QEMU, ESP-IDF 5.5.4, macOS offline analysis, Espressif `esp-coredump` 1.17.2 and Xtensa GDB

The repository CLI reproduced the FreeRTOS task lists from the same retained watchdog and abort session ZIPs. The watchdog dump yielded five tasks and the abort dump yielded six. Both identified `fixture_fault` as the crashed task. A mismatched application ELF, modified manifest, and invalid dump CRC each stopped before invoking the decoder.

- [Reproduction and scope](report.md)
- [Structured execution](run.json)
- [Bounded task evidence](evidence/coredump-task-summary.json)
- [Validation and sandbox controls](evidence/negative-controls-summary.json)

Other boards, dump formats, RISC-V, Device Service HTTP decoding, and physical hardware were outside this validation.

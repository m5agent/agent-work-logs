# Nesso N1 原生 ELF32 UART 转储

- 日期 2026-11-17
- 结果 `PASS`，virtual-device validation
- 工作类型 `code_change`
- 问题来源 原生 ESP32-C6 原会话回执只记录 UART dump 边界
- 源码版本 `7caf061ea74c5275910d3837e61786158cc263b5`

真实 ESP-IDF v5.5.4 来宾分别产生 CRC32 和 SHA-256 转储。两次解码各读回 3 个任务，崩溃任务 PC/SP 与同一 ELF 转储的独立 GDB 读回一致。

- [报告](report.md)
- [结构化记录](run.json)
- [派生证据](evidence/session-core-dump-summary.json)
- [源代码与复现](https://github.com/m5agent/m5stack-esp-emulator/blob/7caf061ea74c5275910d3837e61786158cc263b5/tests/firmware/crash_diagnostics/riscv_c6/README.md)

RISC-V 退栈、任务名和优先级、Flash dump、其他 SDK 及物理硬件未运行。无需设备烧录，未提交 Burner。

[冻结组合版复验](evidence/frozen-combined-summary.json)。冻结组合版再次验证两种 UART 转储的同会话 API/ZIP 与持久回读。

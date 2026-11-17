# ESP32-S3 原生 CPU watchdog 时序回执

- 日期 `2026-11-17`
- 结果 `PASS`（隔离探针、API 与 ZIP）
- 类型 `code_change`
- 版本 `m5stack-esp-emulator @ ee343a14f4097f254d8004967cbbc7c18309573f`
- 环境 原生 Cardputer QEMU、单个专用 watchdog 探针

默认与显式启用诊断各跑同一份固件，两轮均观察到来宾 CPU1 watchdog。启用时收到一条 TIMERGROUP1 和 SYSTIMER 时序摘要，原生 stderr、审核 API 与同会话 ZIP 内容相同。未启用时无该附加回执。两轮均释放 Flash 与租约。

- [报告与复现](report.md)
- [结构化登记](run.json)
- [时序和同会话验证](evidence/watchdog-timing-summary.json)

探针用于验证取证能力。原版 NC1020 的故障根因、真机和浏览器 WASM 未覆盖。未提交 Burner。

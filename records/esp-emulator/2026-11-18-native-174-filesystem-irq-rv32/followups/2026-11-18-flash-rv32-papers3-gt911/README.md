# 原生 Flash 与 UART 崩溃诊断、PaperS3 浏览器触摸复验

- 日期 `2026-11-18`
- 整体 `PARTIAL`，工作类型 `report`
- 基线 `m5stack-esp-emulator@a2148953f1c22a2b2b066780f9c501b3daddcdf0`
- 环境为独立原生 Device Service 和独立 Chromium QEMU WASM 会话

Cardputer ADV 受控来宾把 CRC32 和 SHA256 转储写入实际虚拟 Flash 分区，两种记录均解码出五个任务上下文，并与匹配 ELF 的独立离线结果一致。Nesso N1 两种 UART 转储的 7/4/5 帧与独立 RV32 GDB 一致。PaperS3 Factory V0.5 浏览器触摸的完整图标变化为 4/15，当中的成功、漏点总线记录和帧通路对照均有独立收据。

[报告](report.md) · [结构化结果](run.json) · [取证索引](evidence/README.md)

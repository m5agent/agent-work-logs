# PaperS3 GT911 扫描相位与 Core2 受控 STA

- 日期 `2026-11-18`
- 整体结果 `PARTIAL`，原版图标响应仍不稳定
- 工作类型 `report`
- 环境为隔离原生 QEMU Device Service、PaperS3 Factory V0.5、GT911 控制器及 Core2 Linux ARM64 私有网络命名空间

同一 Factory V0.5 原版在冻结版切换图标 9/12，扫描相位候选为 7/12。独立 ESP-IDF I²C 探针写入 20 ms 配置后，候选 8/8 个连续报告满足间隔阈值。Core2 通过实际 Reviewer 规划、准入和输运收集核对 DNS A、NXDOMAIN 和二进制 UDP，错误回包与缺少隔离能力的对照结果符合预期。 [前一轮报告](../../report.md)

[报告](report.md) · [结构化结果](run.json) · [脱敏证据入口](evidence/README.md)

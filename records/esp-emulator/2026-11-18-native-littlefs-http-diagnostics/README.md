# Core2 与 Nesso N1 LittleFS、Core2 受控 HTTP 和原版诊断

- 日期 `2026-11-18`
- 整体结果 `PARTIAL`
- 工作类型 `report`
- 环境为隔离原生 Device Service、Linux ARM64 受控网络命名空间和板级诊断运行时

Core2 与 Nesso N1 跨独立会话读回各自导出的 LittleFS 分区，原种子对照保持独立。Core2 受控 HTTP 的正向回包与 Host 拒绝分别匹配来宾结果及网络证据。Dial 默认步进通过，快速输入仍漏档。98TAB5 跨两版运行时均未形成可用帧。

[报告](report.md) · [结构化结果](run.json) · [脱敏证据](evidence/README.md)

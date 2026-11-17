# NC1020 跨服务存档与显示归因

- 日期 `2026-11-18`
- 结果存储 `PASS`，显示 `PARTIAL`
- 环境为原版 Cardputer K132、隔离原生 QEMU Device Service 与独立 LCD 诊断探针

两次冷启动使用同一原版与生成后的 Flash，均接受 G0 并保存状态。跨两个新服务阶段导入的存档再次得到来宾读回。画面从一份完整图案、一份局部图案到跨服务的两份无有效图案，仍有独立的显示问题。

[报告](report.md) · [结构化结果](run.json) · [脱敏证据](evidence/README.md) · [原生联合复验](../../report.md)

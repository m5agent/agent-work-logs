# Tab5 UserDemo V0.4 扬声器初始化和 panic 等待

- 日期为 2026-11-18，原版固件启动诊断，结果为 **PARTIAL**。
- 环境为隔离 Device Service 1.90.0 与原生 esp-emu 1.1.0，Tab5 GT911/ILI9881C，属 virtual-device validation。
- 两份同源码重建在匹配符号下都触发 ES8388 初始化断言。基线在随后 panic 的 CPU1 暂停确认处卡住。移除该等待后，普通会话进入软件复位循环。
- 发布 BIN 全程保留，同一 Virtual Device 的正常启动、有效画面和音频仍未通过。实体硬件、浏览器、Burner 未执行。

[报告](report.md) · [结构化执行清单](run.json) · [固件和会话证据](evidence/userdemo-wfi-source-ab-summary.json)

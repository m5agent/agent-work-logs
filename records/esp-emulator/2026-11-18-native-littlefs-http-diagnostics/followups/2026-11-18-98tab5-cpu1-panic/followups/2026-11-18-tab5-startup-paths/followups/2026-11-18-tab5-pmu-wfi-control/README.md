# Tab5 双核 PMU 暂停与 WFI 对照

- 日期为 2026-11-18。结果为 PASS，限固定 SDK 夹具的暂停、唤醒与继续执行。
- 环境为隔离 Device Service 1.90.0、Tab5 原生 esp-emu 1.1.0，验证类型为 virtual-device validation。
- 原版背景见 [Tab5 三份原版启动路径复验](../../README.md)。

一个 CPU1 忙循环会话和两个 WFI 冷启动会话均在 CPU0 发出 PMU 暂停请求后停止进展，并在解除暂停后恢复。忙循环的暂停状态位变为 1。WFI 路径中状态位一直为 0，期间发出的中断等到解除暂停后才被处理。UserDemo 启动故障仍待归因。[完整报告](report.md) · [执行记录](run.json) · [证据回执](evidence/busy-vs-wfi.summary.json)

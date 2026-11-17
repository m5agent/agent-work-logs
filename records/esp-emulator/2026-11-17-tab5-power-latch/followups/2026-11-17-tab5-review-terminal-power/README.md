# 原版 Tab5 终端关机审核

- 日期 2026-11-17
- 结果 `PARTIAL`。同来宾终端关机通过，原版完整交互仍有未执行项。
- 工作类型 `code_change`
- 问题来源 审核把预期关机的 HTTP 409 当作普通输入失败，观察窗口也可能在关机后开始。
- 审核实现 `c721839882d4dda958ec595f0e1b4071375c9276`，详情页 `57b38a3a6ffe4fda1ec9da3a9170eb8bf1c6f161`
- 环境 虚拟设备验证，隔离 Device Service，Tab5 ST7123，无 ELF，原版 Arduventure 1.0.0。

新版在 60.257 秒有效观察后执行实际电源键长按。虚拟 EN 状态、原版关机帧和证据 ZIP 均现场核验。独立 Chromium 实际渲染详情页，显示终端关机通过。普通中心长按未执行，整个审核仍为 `E_INTERACTION_CLAIM_PARTIAL`。

- [报告](report.md)
- [结构化记录](run.json)
- [旧版对照](evidence/legacy-control-summary.json)
- [原版复审](evidence/candidate-replay-summary.json)
- [详情页检查](evidence/dashboard-summary.json)

本次未运行物理电源、其他 Tab5 触控芯片、冷恢复、并发压力或 Burner 提交。

冻结组合版在 60.012 秒运行观察后验证了同一原版的请求、关机帧和 ZIP 末态。 [冻结组合版复验](evidence/frozen-combined-summary.json)

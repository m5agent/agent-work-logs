# Reviewer 0.31 首次常驻 Core2 独立快照验证

- 结果：`PARTIAL`（严格八次有效移动）；标准审核终态为 `done / SIM_VERIFIED`。
- 实测：仅一次授权请求，`202 / queued=1`，七次合法移动覆盖四方向。
- 保留：首个右移因棋盘已经靠右而为 `NOT RUN / no_legal_move`，没有发送该步输入；后续实际右移通过。未追加请求补跑。
- 范围：`virtual-device validation`，父记录和旧证据保留；物理硬件、浏览器和其他板卡 `NOT RUN`，未提交 Burner。
- 文件：[报告](report.md)、[执行](run.json)、[证据摘要](evidence/resident-core2-canary.summary.json)。
- 前序：[隔离快照克隆验证](../../report.md)。

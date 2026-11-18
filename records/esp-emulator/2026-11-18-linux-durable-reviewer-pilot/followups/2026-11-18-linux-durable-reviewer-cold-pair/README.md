# Linux 持久审核卷冷启动回读与重试

- 日期 `2026-11-18`
- 结果 `PASS`，范围为无虚拟网卡的隔离 Linux 来宾冷启动后保留审核状态与证据
- 工作类型 `infra_baseline`
- 问题来源为原生 Linux 审核 worker 持久化验收
- 源码采用 Device Service `a729e24b1e4724b783ab2d59eec689cfdfeb24b3` 与 Reviewer `a295e0173a0e3157c120de8ba6fcec128aa665c1`

同一 VirtioFS 卷保存了原版 CardputerDict 0.6.4 的审核。关闭来宾并冷启动后，标准重试前先回读原任务、已停止的会话、同一 ZIP 和 PCAP，所有租约均为零。正常重试随后以同一原版固件启动新会话，完成受控传输验证并清理。

[执行报告](report.md) · [运行记录](run.json) · [有界证据](evidence/cold-pair.summary.json)

本次覆盖已完成任务的冷启动恢复。独立的低磁盘中断对照仍保留。可信 HTTPS 发音、PCM、物理设备及常驻 Linux 部署未运行。没有 Burner 提交。

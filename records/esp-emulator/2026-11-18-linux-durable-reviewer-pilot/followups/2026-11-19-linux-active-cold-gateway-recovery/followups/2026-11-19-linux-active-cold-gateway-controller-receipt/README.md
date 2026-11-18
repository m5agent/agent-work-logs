# Linux 活动审核冷启动恢复与宿主停机凭据

- 日期为 2026 年 11 月 19 日（UTC+08:00）。
- 结果为虚拟设备验证 PASS，范围为原版 CardputerDict 0.6.4、具名网关和可信宿主停机凭据。
- 工作类型为代码修复和原版固件 dry-run。
- Device Service 1.99.0 候选为 `97339c1137e4e8564114e7476ba607f1129fe68c`，Reviewer 0.27.0 为 `f0101b6bb0926a69ef2f8477ae81e991338391f5`。
- 环境为无网卡 Linux ARM64 VZ、持久 VirtioFS 和初代 Cardputer 的原生 `qemu-wifi`。

在旧审核仍持有一个租约时，宿主停止了原虚拟机。新 Linux 内核先在未提供停机凭据时复现 HTTP 409 和租约保留。随后在同一次 Linux 启动中提供宿主凭据，旧租约和可写 Flash 得到释放，原版标准重试进入 `SIM_VERIFIED`。SD 缓存为 10,605 字节 MP3，证据 ZIP 与 API 均读到同一段 84,992 字节 PCM。

旧网关及隔离记录字节保持一致，两份旧会话 ZIP 的 PCAP 与异常停机后的实盘 PCAP 相同。两台独立测试虚拟机均已退出，租约为零。常驻 Linux 部署、实机和 Burner 提交未执行。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏证据摘要](evidence/linux-active-cold-gateway-controller-receipt.summary.json)

# Device Service 与 Reviewer 同时中断后的审核恢复

- 日期 2026-11-18（UTC+08:00）。
- 类型 Linux 隔离环境的原生虚拟设备回归。
- 范围 保存快照 dry-run、两个服务均被 SIGKILL 后的重启顺序、原会话清理和同固件重试。

旧版在精简 Linux 上先重启 Device Service，审核恢复为服务错误，旧来宾和网络监督进程仍存活，且标准重试已获准。另一组带 procps 的对照先重启 Reviewer。Device Service 后上线并清理旧来宾后，审核在自动观察窗口结束时仍留下待协调结果，之后标准重试获准。两组的进程工具环境和启动顺序都有差异。

Device Service 1.96.0 和 Reviewer 0.26.0 在隔离 Linux 重跑两种启动顺序，均在用户重试前完成旧会话进程、命名空间、Flash 和租约回收。Reviewer 先启动时先如实记录设备服务离线，待设备服务启动后自动完成协调。两次均保留同会话证据，标准重试各创建一个新会话，STA 数据链路通过。无界面 SDK 固件的综合审核仍为 `manual_review / E_NO_FRAME`。

[报告与复现](report.md) · [结构化记录](run.json) · [Linux 候选回执](evidence/linux-paired-restart-release.summary.json) · [旧版两组回执](evidence/baseline-double-service-recovery.summary.json) · [此前仅重启 Reviewer 的验证](../2026-11-18-reviewer-active-create-recovery/README.md)

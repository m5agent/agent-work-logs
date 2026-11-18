# Reviewer 中断后的 Device Service 会话创建恢复

- 日期：2026-11-18（UTC+08:00）。
- 工作类型：已执行的原生虚拟设备回归。
- 范围：保存快照 dry-run、审核进程崩溃后的 create 协调，以及之后的标准重试。
- 版本：Device Service 1.95.0 与 Reviewer 0.25.0。

macOS 隔离复验用同一原版 Core2 2048 镜像覆盖两种中断位置。已创建的会话释放可写 Flash 和租约，停止后仍能读证据，并行会话维持原进程与租约。尚未进入 Device Service 的旧创建在恢复后返回 HTTP 409，未分配会话。标准重试启动新会话，游戏四方向棋盘验证通过，终态为 `SIM_VERIFIED`。

ARM64 Linux 隔离虚拟机使用同一份 Cardputer ADV STA 固件做版本 A/B。旧版重启后仍持有来宾、命名空间和租约，需显式停止。新版自动回收并保留 53 个数据包的原始抓包。标准重试只创建一个新会话，STA 应用数据链路通过，无界面测试固件的审核终态保留 `manual_review / E_NO_FRAME`。

[报告与复现](report.md) · [结构化记录](run.json) · [macOS 同原版回执](evidence/macos-create-recovery.summary.json) · [Linux A/B 回执](evidence/linux-reviewer-restart-ab.summary.json) · [原有 Linux 空闲重启验证](../2026-11-18-linux-worker-idle-restart/README.md)

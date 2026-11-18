# Linux 活动审核的异常关机恢复

- 日期为 2026 年 11 月 19 日（UTC+08:00）。
- 虚拟设备验证中，活动会话恢复和标准重试为 `FAIL`，旧证据读回为 `PASS`。使用原版固件复现。
- 工作类型为服务恢复诊断，范围为独立 Linux ARM64 VZ 和持久 VirtioFS 卷。
- Device Service 为 `09db00eb793972a679f87234a6797eff70334d47`，Reviewer 为 `f0101b6bb0926a69ef2f8477ae81e991338391f5`。

异常关机前，原版 CardputerDict 0.6.4、具名网关和一个活动租约已实测。重启后旧内核资源已消失，旧审核显示 `E_SERVICE_RESTART`。Device Service 仍保留一个租约和可写 Flash，旧证据 ZIP 可下载，标准保存快照重试返回 HTTP 409。

[报告](report.md) · [机器记录](run.json) · [脱敏证据摘要](evidence/linux-active-cold-gateway-recovery.summary.json)

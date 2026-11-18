# Linux 宿主停机凭据的独占和信任边界复验

2026 年 11 月 19 日（UTC+08:00），在真实 Linux ARM64 VZ 和同一原版 CardputerDict 0.6.4 上完成虚拟设备验证。独占与凭据拒绝对照均通过。连续保留旧会话证据，合法交接后原版标准重试达到 `SIM_VERIFIED`。

实际旧来宾持有一个租约时，独立启动器尝试从原路径和别名接入同一试验卷，两次均在启动 VZ 前退出。控制器拒绝旧 VM incarnation 和另一卷的停机确认副本。新 Linux 启动中，用旧网关真实记录构造的准确凭据，直接置于恢复状态或通过指向该状态的符号链接提供，都在服务监听前被拒绝，旧记录和 PCAP 字节保持一致。

[执行与边界](report.md) · [机器记录](run.json) · [脱敏证据摘要](evidence/controller-exclusivity.summary.json) · [此前标准冷启动恢复验收](../../README.md)

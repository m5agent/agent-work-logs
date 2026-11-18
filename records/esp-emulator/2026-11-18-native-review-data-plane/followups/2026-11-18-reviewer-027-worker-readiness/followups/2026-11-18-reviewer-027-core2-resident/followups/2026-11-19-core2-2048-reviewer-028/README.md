# Core2 原版 2048 Game 1.0 的 Reviewer 0.28.0 四向复验

2026 年 11 月 19 日（UTC+08:00），同一 505,760 字节原版应用通过隔离 Device Service 1.99.0 和 Reviewer 0.28.0 的标准保存快照 dry-run，终态为 `done / SIM_VERIFIED`。上下左右各完成两个合法移动，八步均从同一会话的实际帧读回棋盘。记录还验证了格式错误的结构化输入断言在排队与租约创建前被拒绝。

应用字节、运行时与证据 ZIP 的身份一致。租约归零，可写 Flash 已释放，原生 QEMU 和隔离服务均退出。实体 Core2 与浏览器 WASM 为 `NOT RUN`，Burner 未提交。

[复现及证据边界](report.md) · [执行记录](run.json) · [脱敏摘要](evidence/core2-2048-review028.summary.json) · [上一版隔离与常驻回读](../../README.md)

# All Day Watch 原版在 Device Service 1.99 的浅睡唤醒复测

2026-11-18，StickS3 原版固件在隔离的原生 QEMU 会话中执行了此前保留的 A、B 点按和 B 长按序列。QMP 观察到客体挂起。通过 Device Service 点按 B 后，0.439 秒内观察到运行，随后取得新的 135 × 240 非黑帧。唤醒后观察 65.117 秒，串口无 panic 或软件复位，崩溃诊断返回 `no_evidence`。

本次虚拟设备验收覆盖一次 GPIO 浅睡与唤醒。物理 StickS3、外部 32.768 kHz 慢钟及其他深睡唤醒源为 `NOT RUN`。

- [执行方法与限制](report.md)
- [结构化记录](run.json)
- [同会话验证摘要](evidence/current199-watch-bounded.summary.json)
- [先前 GPIO 模型与原版对照](../../README.md)

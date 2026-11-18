# Dial R1F30 原版在 8 ms 的漏选复验

2026-11-18，**PARTIAL**，原生虚拟设备验证。三次冷启动使用同一未修改的 vinylM5Dial 1.0 R1F30 BIN，绑定 Device Service 1.97.0、实际 GPIO 控制器和 PORT.B AudioPlayer 的 N9301 UART。

两次整圈复验里，5、12、20 与默认 35 ms 各通过 8/8。8 ms 为 7/8。漏选的正向 16 格交付了 64 个 GPIO 边沿，原版发出有效的第 7 轨指令，预期为第 1 轨。第三次按历史混合动作复验，5 和默认 35 ms 各通过 9/9。保留此前的 5 ms 漏选，稳定的最短间隔尚未确定。

[报告与复现](report.md) · [结构化记录](run.json) · [本轮逐动作回执](evidence/dial-r1f30-197-cadence.summary.json)

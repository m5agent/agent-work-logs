# M5TabOS 原版空闲任务与定时中断

- 日期为 2026-11-18。结果为 PARTIAL。
- 环境为 Tab5、隔离 Device Service 1.90.0、原生 esp-emu 1.1.0，验证类型为 virtual-device validation。
- 固件为 M5TabOS 0.9.1 原版。镜像、归一化 Flash、源码和运行时的固定哈希见回执。

CPU0、CPU1 分别处在 FreeRTOS 的 IDLE0、IDLE1。两核各自的 SYSTIMER 中断处理计数持续增长，调度 tick 也持续增长。三轮均未取得完整画面。应用任务的首个阻塞条件仍待查明。[完整报告](report.md) · [执行记录](run.json) · [原版会话回执](evidence/tabos-idle-systimer.summary.json)

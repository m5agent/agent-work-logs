# AtomS3 #235 原版黑帧与同机型对照

- 日期 `2026-11-19`（UTC+08:00）
- 结果 三款原版黑帧复现及官方 UIFlow2 对照通过，根因仍为 `PARTIAL`
- 环境 原生虚拟 AtomS3 ST7735S、Device Service 1.99.2、同一冻结 QEMU
- 问题来源 [Issue #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)

Spirit Level、Motion Face 和 Pocket Clock 原版各运行约 60 秒。每轮 30 张 128×128 取样帧均全黑，均有 MPU6886 活动，GP-SPI 传输与面板记录均为 0。同一默认机型的官方 UIFlow2 在 16 秒内有 6 张非黑帧及 9,838 条 SPI 传输。

Spirit 轮的可选 UART 应用偏移行未出现，脚本状态保留为 `REVIEW`。四轮均保留同会话 ZIP，停机后可写 Flash 已释放、租约为零。具体 RDDID 位序、来宾板型探测返回和实体硬件尚未验证。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏证据](evidence/atoms3-235-paired-baseline.summary.json) · [早期基线](../../README.md)

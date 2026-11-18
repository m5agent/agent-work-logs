# Tab5 UserDemo I2S1 采集的复位与停机

- 日期为 2026-11-18。验证类型为 virtual-device validation。
- 结果为 `PASS`。原版 UserDemo V0.4 的显式采集会话复位后启动了新的 P4 进程，替换 WAV，同时保留会话及原租约到期时间。
- 停机后最终 PCM 与原生 WAV、HTTP 回读和证据 ZIP 一致。全程无来宾输入。
- 本轮跟进 [Device Service 1.92 的原版音频采集](../../README.md)。

[完整报告](report.md) · [执行清单](run.json) · [复位回执](evidence/reset-lifecycle.summary.json)

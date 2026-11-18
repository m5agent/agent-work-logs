# StickS3 的 RC_FAST/256 RTC 慢钟

2026-11-18 · 原生 StickS3 · virtual-device validation

修正 RTC 慢计数与 Timer Group 校准使用不同速率的问题。同一份 RC_FAST/256 镜像请求 500 ms 定时浅睡，旧运行时实际挂起约 1.077 秒，最终 1.94 冻结包为 493.389 ms。默认慢钟、定时深睡、原版 Watch 和浅睡生命周期对照通过。

[验证报告](report.md) · [机器记录](run.json) · [冻结包证据](evidence/rtc-frozen-194.summary.json)

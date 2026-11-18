# Device Service 1.99.0 冷启动恢复修订的常驻回读

2026 年 11 月 19 日（UTC+08:00）的 macOS 协调切换及独立回读为 `LIVE_VERIFIED`。工作台和审核侧均在 `9837c3f84df4383eb74881a1f44fcd3f460daefa` 提供同一份 Device Service OpenAPI 1.99.0，保留 55 和 98 条会话。Reviewer 0.27.0 保留 129 条记录和抽样证据。

两套 macOS 常驻启动参数均未启用 Linux 宿主停机凭据。本次以 [隔离 Linux 同原版的功能验证](../../README.md) 为发布依据。生产来宾和 Linux 常驻切换均为 `NOT RUN`，Burner 未提交。

[回读报告](report.md) · [运行记录](run.json) · [脱敏证据摘要](evidence/resident-readback.summary.json)

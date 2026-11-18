# Reviewer 0.28.0 原版 ADV 发音审核的常驻回读

2026 年 11 月 19 日（UTC+08:00），修订版 `37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1` 的常驻切换和独立读回为 `LIVE_VERIFIED`。Reviewer 0.28.0 在既有 macOS 审核后端就绪，两套 Device Service 1.99.0 角色保持原版本。

首次切换在常驻 Python 3.9.6 上导入失败，受保护的回退恢复了 Reviewer 0.27.0。129 条历史、数据库与抽样 ZIP 均通过核对。修订后保留了 Python 3.9.6，并在隔离服务健康验证和同一原版执行后进行第二次切换。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏证据](evidence/resident-readback.summary.json) · [标准审核原版验证](../../README.md)

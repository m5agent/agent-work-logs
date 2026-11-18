# XIAOZHI 审核阶段归因与 Core2 原版回归

- 日期 `2026-11-18`
- 模型准入归因 `PASS`
- Core2 2048 同原版 dry-run `SIM_VERIFIED`
- Reviewer 候选 `f0101b6bb0926a69ef2f8477ae81e991338391f5`，OpenAPI 版本 `0.27.0`

使用同一份 XIAOZHI 1.1 元数据提交两次真实审核 HTTP dry-run。请求 AI 审核与直接审核均给出 `manual_review / E_NO_SIM_PROFILE`，归因为 `unsupported_target`。该固件功能保持 `NOT EVALUATED`，审核未下载 BIN 或创建来宾。

同候选版的 Core2 原版 2048 完成上下左右棋盘变化验证。证据 ZIP 校验通过，临时 Flash 与活动租约归零。常驻 Reviewer 已完成就绪、历史和证据读回。两条验证路径均未提交 Burner。

[执行报告](report.md) · [机器可读记录](run.json) · [准入证据](evidence/model-admission.summary.json) · [Core2 证据](evidence/core2.summary.json)

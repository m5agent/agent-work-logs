# Nesso 触摸修复上游交付

- 日期：`2026-11-13`
- 结果：`PASS`（PR 交付及远端回读）；合并为 `NOT RUN`。
- 工作类型：`code_change`
- 问题来源：原记录 [源码对照](../../README.md)。
- 源码版本：M5GFX `7d3d0342b9453a78db14451575c40d8fe564b659`，base `28d47949bdc84f30881623476f555398e2194313`。
- 环境：GitHub 远端交付；没有新增 guest 或物理硬件运行。

[上游 PR #416](https://github.com/m5stack/M5GFX/pull/416) 已创建，远端 head 与预期 commit 一致，diff 仅一文件一行。PR 引用公开固定 SHA 的完整验证记录。候选源码与此前实际执行的 master 修复控制逐字节一致。

[report.md](report.md) 记录交付边界，[run.json](run.json) 记录远端身份。原版 BIN 仍 FAIL；上游合并、新版发布与 Burner 提交均未执行。

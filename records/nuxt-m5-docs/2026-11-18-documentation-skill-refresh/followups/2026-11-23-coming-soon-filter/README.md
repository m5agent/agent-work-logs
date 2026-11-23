# 文档 Skill 过滤 Coming Soon 页面

| 项目 | 结果 |
| --- | --- |
| 日期 | 2026-11-23，Asia/Shanghai |
| 工作类型 | `code_change` |
| 问题来源 | 文档 Skill 更新需求 |
| 源码版本 | `nuxt-m5-docs@74ccbb789062fc43b74e2673b115fbeb0c19af87` |
| 环境 | ARM64 Linux 虚拟机，Python 3.12.16 |
| 结果 | PASS |

`m5stack-assistant-local` 的更新流程从正文包和查询索引中排除了 45 篇含 Coming Soon 标记的文档。新版经过 Linux 虚拟机验证，已发布至 Skill Hub，回读的 4,401 个文件与构建产物一致。

- [文档 Skill 发布记录](../../README.md)
- [执行报告](report.md)
- [运行记录](run.json)
- [验证摘要](evidence/coming-soon-filter-summary.json)

验证覆盖 Skill 的本地查询与分发。固件、实机和面向终端用户的问答服务不适用于本次构建改动。

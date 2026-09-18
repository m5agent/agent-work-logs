# AGENTS.md

本仓库分两层发布，开始工作前必须先确定记录属于哪一层。

| 层 | 目录 | 发布目标 |
| --- | --- | --- |
| 对外 | `records/` | 内部 GitLab + 公开 GitHub |
| 内部 | `internal/records/` | 仅内部 GitLab |

判断标准只有一个：**这条记录对外部读者有价值吗？** 没有就放 `internal/`。拿不准也放 `internal/`。

配置本机或内网服务、安装工具、调整访问控制、盘点内部权限、排查内网服务——都属于 `internal/`，
**不要**放进 `records/`。

## 前置阅读

- [docs/work-record-workflow.md](docs/work-record-workflow.md)
- [docs/record-format.md](docs/record-format.md)
- [docs/redaction-policy.md](docs/redaction-policy.md)

## 何时留档

- 处理了公开仓库的 Issue、PR/MR，并做了可验证的分析、复现、修复或验收；
- 执行了实机构建、烧录、测试、压测或回归；
- 完成了代码改动、评审或跨仓库对比分析；
- 排查了服务或环境问题且结论依赖实测证据（按上面标准决定层次）；
- 用户明确要求形成报告。

只读查看、解释现象或简短问答不需要留档。

## 新增记录时

- 对外：`records/<target-slug>/<YYYY-MM-DD>-<topic>/`
- 内部：`internal/records/<target-slug>/<YYYY-MM-DD>-<topic>/`
- 从 `templates/work-record/` 复制基础文件，补齐 `README.md`、`report.md`、`run.json`、`evidence/`。
- 更新对应层的 README 索引；对外记录还要更新根 README 索引。
- 结论必须来自真实构建、日志、协议帧、任务记录或实机行为，不得由单次工具返回的 `passed`
  推断应用层结论。
- patch 必须能对声明的 base commit 通过 `git apply --check`。
- 同一问题的复测追加独立 evidence 和 follow-up execution，不覆盖原始记录。

## 发布

```bash
./scripts/publish.sh
```

脚本先推 GitLab（完整内容），再把公开子集重建为单个提交强制推送 GitHub。公开仓库是生成产物，
**不要**直接往 GitHub 推内容，也不要手工修改公开仓库历史。

发布后确认：GitLab 侧 `HEAD...origin/main` 为 `0 0`；公开仓库只含 `records/`、`docs/`、`templates/`
和根文件，且不含任何 `internal/` 内容。

## 引用

对外回复 Issue、PR/MR 时使用公开仓库的固定 commit 链接。内部同事交流使用内部 GitLab 链接。
不要用内部 GitLab 链接回复公开 Issue。

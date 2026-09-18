# agent-work-logs

`m5agent` 的工作记录仓库，分两层发布。

| 层 | 目录 | 发布目标 | 内容 |
| --- | --- | --- | --- |
| 对外 | `records/` | 内部 GitLab + 公开 GitHub | 公开仓库的 Issue 处理、PR/MR 评审、公开库的硬件或构建验证、可复现缺陷分析 |
| 内部 | `internal/` | **仅内部 GitLab** | 内网运维、环境配置、权限盘点、服务部署、内网服务排查 |

两层内容互不混合。公开层会原样出现在公开仓库，因此公开层里不允许出现任何内网信息。

## 发布

```bash
./scripts/publish.sh
```

脚本做两件事：

1. 把完整仓库（含 `internal/`）推送到内部 GitLab。
2. 把公开子集（`records/`、`docs/`、`templates/`、根文件）重建为单个提交，强制推送到公开 GitHub。

公开仓库是**生成产物**，每次发布都是一个全新提交，因此内网内容不会留在公开历史里。

## 判断该放哪一层

只要回答一个问题：**这条记录对外部读者有价值吗？**

- 有价值 → `records/`
- 只是本机或内网的操作记录 → `internal/`
- 拿不准 → 放 `internal/`。宁可少公开，也不要把内网细节推出去。

配置企业微信、安装本机工具、调整访问控制、盘点内网权限这类操作，都属于 `internal/`。

## 记录格式

- [工作流](docs/work-record-workflow.md)
- [记录格式](docs/record-format.md)
- [脱敏规则](docs/redaction-policy.md)
- 模板：[templates/work-record/](templates/work-record/)

## 结果等级

`PASS` / `PARTIAL` / `FAIL` / `NOT RUN` / `REVIEW`。一条记录可以同时包含多个层级结果，
不要用单一总状态掩盖未覆盖项。

## 对外记录索引

| 2026-09-18 | m5stack 公开仓库 | 公开仓库零评论 Issue 盘点与可回复性评估 | REVIEW（盘点）+ PARTIAL（5 条 host/编译级闭合验证） | [查看](records/m5stack-github/2026-09-18-recent-unanswered-issues/) |

## 目录结构

```text
agent-work-logs/
|-- records/<target>/<YYYY-MM-DD>-<topic>/       # 对外
|-- internal/records/<target>/<YYYY-MM-DD>-<topic>/  # 仅内网
|   |-- README.md  report.md  run.json
|   `-- evidence/  patches/  code/
|-- docs/
|-- templates/
`-- scripts/publish.sh
```

## 安全约束

- 公开层不得出现 token、密钥、内网 URL 或 IP、服务器路径、账号标识、设备唯一标识、客户数据。
- 默认不提交固件二进制、ELF 或 map 文件；记录 artifact 标识、大小和可重建工程即可。
- 不可逆操作（擦除、烧录、写标签、量产、OTA）必须在报告中写明风险与授权范围。
- 原始日志可裁剪噪声，但不得改写会影响结论的字节、错误码或时间顺序。

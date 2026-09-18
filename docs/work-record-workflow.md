# 工作记录、归档与发布工作流

## 适用范围

本流程适用于 `m5agent` 承担的全部可验证工程工作：Issue 处理、PR/MR 评审、代码改动、
硬件实机验证、服务排障、环境基线盘点。目标是把结论从对话和临时系统中解放出来，变成可复查、
可重建、可继续追加的记录。

用户只要求查看、解释或只读诊断时，不自动发布。用户要求实际执行、复测、修复或验收时，
默认完成本流程并推送；用户明确要求仅本地时除外。

## 先决定发布层

| 层 | 目录 | 发布目标 |
| --- | --- | --- |
| 对外 | `records/` | 内部 GitLab + 公开 GitHub |
| 内部 | `internal/records/` | 仅内部 GitLab |

判断标准：这条记录对外部读者有价值吗？没有或拿不准 → `internal/records/`。
配置本机或内网服务、安装工具、调整访问控制、内网权限盘点都属于内部层。

## 前置阅读

开始前必须读取：

- [记录格式](record-format.md)
- [脱敏规则](redaction-policy.md)

## 固定位置

- 本地仓库：`~/Documents/agent-work-logs`
- 内部远端（完整内容）：内部 GitLab 的 `dev.bot/agent-work-logs`
- 公开远端（生成产物）：`https://github.com/m5agent/agent-work-logs`
- 对外记录目录：`records/<target-slug>/<YYYY-MM-DD>-<topic>/`
- 内部记录目录：`internal/records/<target-slug>/<YYYY-MM-DD>-<topic>/`
- 基础模板：`templates/work-record/`

不要在源码仓库中暂存本仓库的文件，也不要批量暂存源码仓库的用户改动。

## 1. 明确目标和验收层级

开始前记录四项：

1. **目标**：要证明的用户行为或工程结果。
2. **上下文**：问题来源、仓库与 base commit、芯片或板卡、外设、服务版本、依赖。
3. **约束**：兼容范围、资源限制、禁止修改项、设备状态变更边界、授权范围。
4. **验收**：每一层如何判定通过。

按工作类型选择验收层级，未发生的层级不要编造：

| 层级 | 含义 |
| --- | --- |
| `build` | 源码能否构建，产物是否合法 |
| `flash` | 固件或镜像是否成功写入并重启 |
| `transport` | UART/I2C/SPI/USB/HTTP 等链路是否真实收发 |
| `device_response` | 外设或服务是否返回协议级有效响应 |
| `data_behavior` | 数据是否随输入、地址或状态正确变化 |
| `visual_or_physical` | 屏幕、LED、继电器、传感器或机械行为是否符合预期 |
| `review` | 只完成阅读、分析或评审，无可执行验证 |
| `delivery` | 代码、报告、PR/MR 是否已按授权交付 |

每层单独使用 `PASS`、`PARTIAL`、`FAIL`、`NOT RUN` 或 `REVIEW`。

## 2. 先取证，再修改

- 读取真实 Issue、PR/MR、源码、最近 diff、构建配置、日志和官方协议或数据手册。
- 调试按“现象分类 → Top 3 假设 → 证据 → 最小实验 → 修改”推进。
- 修复保持最小并保护公共 API；patch 必须声明上游仓库和 base commit。
- 引用外部资料时使用永久链接或明确版本，不要引用会漂移的页面标题。

## 3. 执行与取证

- 保存完整环境、命令、依赖版本和资源占用结果。
- 硬件操作前先读取 `device-test-center` skill，调用一次 overview 选择在线、空闲且匹配的设备。
- 烧录、擦除、写标签或其他不可逆操作必须先获得用户确认。
- 记录 artifact ID、SHA256、大小、任务 ID、任务终态、session ID 和关键时间戳。
- 任务的 `passed` 只证明任务计划完成；应用行为必须由串口标记、协议帧、数据匹配、测量或
  相机证据单独证明。
- 串口默认只取尾部片段；需要完整审计时才取全量，并记录 bytes、chunks、dropped、truncated。

## 4. 建立归档

```text
records/<target-slug>/<YYYY-MM-DD>-<topic>/
|-- README.md      # 快速结论、关键任务和文件导航
|-- report.md      # 根因、修复、执行、证据、边界和回滚
|-- run.json       # 机器可读的结构化记录
|-- evidence/      # 原始日志、协议帧、测量、事件摘要、图片
|-- patches/       # 可直接应用的最小修复
`-- code/          # 可重建的测试或复现工程
```

同一问题的后续复测追加 follow-up execution 和独立 evidence，不覆盖首次运行。修正结论时保留
时间线并说明哪些状态发生变化。

## 5. 公开前脱敏

两个远端中的公开仓库对所有人可见，因此每条记录提交前都必须通过
[脱敏规则](redaction-policy.md) 的检查清单。需要隐藏唯一标识时，保留有序的脱敏摘要，并记录
原始数据 SHA256、任务 ID、session ID 和字节数。文件名应包含 `redacted` 或 `summary`。
脱敏内容不得标记为 raw。

## 6. 提交前验证

至少执行：

1. `git diff --cached --check`。
2. 所有 JSON 可解析。
3. 文本可严格按 UTF-8 解码且无 BOM。
4. Markdown 相对链接全部存在。
5. 敏感信息扫描无命中。
6. patch 对声明的 base commit 通过 `git apply --check`。
7. `git status` 只包含本次记录文件。

验证应与风险匹配。纯 follow-up 不需要重复未变化的构建，但必须把新增统计与原始任务自动比对。

## 7. 提交、推送与远端回读

提交到 `main`，然后用发布脚本推送：

```bash
./scripts/publish.sh
```

脚本把完整内容推到内部 GitLab，再把公开子集同步到公开 GitHub 并追加提交（保留线性历史）。完成条件：

- 本地工作区干净；
- GitLab 侧 `HEAD...origin/main` 为 `0 0`；
- 公开仓库只包含公开子集，且不含任何 `internal/` 内容。

## 8. 对外引用边界

**只引用公开仓库的链接。** 公开层记录用公开仓库的固定 commit 链接；内部 GitLab 链接不得出现在
公开 Issue、公开 PR 或任何外部可见的回复中。

在公共 Issue 或 PR 中回复时：

- 只有任务明确要求时才回复，不擅自关闭 Issue、创建 PR 或推送上游分支；
- 先推送记录，再评论；
- 使用完整 commit SHA 的固定链接；
- 明确写出 `PARTIAL`、`NOT RUN`、`REVIEW` 等真实限制；
- 不泄露内部系统、凭据、内网端点和无关的安全细节。

内部同事回复可以使用内部 GitLab 链接，但内容边界与公开仓库相同。

## 9. 最终交付

最终回复至少说明：仓库、commit、报告链接、patch（如有）、关键 evidence，以及验证通过项与剩余
风险。任何无法执行的验证都要说明原因和补测条件。

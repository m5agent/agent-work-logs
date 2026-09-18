# 工作记录格式

## 目标

每条记录应让未参与的人能够回答四个问题：做了什么、使用了什么环境、观察到了什么、
还有什么没有验证。

## 存放位置

| 层 | 目录 | 发布目标 |
| --- | --- | --- |
| 对外 | `records/<target-slug>/<YYYY-MM-DD>-<topic>/` | 内部 GitLab + 公开 GitHub |
| 内部 | `internal/records/<target-slug>/<YYYY-MM-DD>-<topic>/` | 仅内部 GitLab |

不确定就放内部层。

## 必备内容

### README.md

快速浏览入口：目标、结论、关键证据、目录导航和剩余限制。填写
[模板](../templates/work-record/README.md) 中的全部字段，不适用的字段写“不适用”并说明原因。

### report.md

完整报告，至少包含：

- 问题来源和现象，或任务背景与目标；
- 假设与实际根因（无法定根因时写“未定位”并说明证据边界）；
- 改动范围、兼容性和影响面；
- 构建或运行环境及命令；
- 执行过程与证据；
- 未覆盖项、风险和回滚方式。

### run.json

机器可读的单次记录。字段可扩展，但**不要删除** `schema_version`、`kind`、`source`、
`hardware`、`firmware`、`execution` 和 `checks`。

非硬件工作把 `hardware` 和 `firmware` 写成空对象或省略字段值，但保留键。

### evidence/

能独立支撑结论的原始证据：日志、协议帧、任务事件摘要、测量数据、截图或报告导出。
日志应标注来源和采集时间；图片保留原始文件或记录 SHA256。

### patches/

文件名使用顺序号，例如 `0001-fix-uart-timeout.patch`。记录 base commit 并验证：

```bash
git apply --check patches/0001-fix-uart-timeout.patch
```

### code/

可重建的测试、复现或 HIL 工程。固定依赖版本，不提交大型构建产物。

## 结果等级

- `PASS`: 在声明的验收层级通过，并有原始证据。
- `PARTIAL`: 部分核心步骤通过，但仍缺少会影响最终结论的验证。
- `FAIL`: 已执行，目标行为未通过。
- `NOT RUN`: 因条件不足没有执行。
- `REVIEW`: 只完成阅读、分析或评审，没有可执行验证。

## 可追溯性

- 外部 issue、PR/MR、数据手册和源码使用永久链接或明确版本。
- 记录 Git commit、artifact ID、task ID、session ID 和 SHA256。
- 时间使用 ISO 8601，并写明时区或使用 UTC。
- 测试基础设施故障与被测对象故障分开描述。
- 引用他人原文时标注来源，不复制受限内容。

# <对象> <工作主题>

- 日期：`YYYY-MM-DD`
- 结果：`PASS | PARTIAL | FAIL | NOT RUN | REVIEW`
- 工作类型：`issue | pr_review | code_change | hardware_test | service_debug | infra_baseline | report`
- 问题来源：`公开 URL 或内部编号（可公开时填写）`
- 源码版本：`repository @ commit`
- 环境：`主机、外设、服务版本、连接方式；不写内网端点`

## 结论

用一段话说明目标是否达成，以及结论覆盖到哪个验收层级。

## 关键证据

- 构建或运行：
- 产物或部署：
- 实机或服务执行：
- 日志、测量或协议：

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：原始证据
- `patches/`：修复 patch
- `code/`：可重建工程

## 未覆盖项

列出没有执行的验证及原因，不要将其隐藏在 PASS 结论中。

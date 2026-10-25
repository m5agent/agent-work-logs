# ESP Emulator current-state and documentation contract ownership

- 日期：`2026-10-25`
- 结果：`PASS`（代码/文档组织与契约）；固件功能、QEMU runtime 和 physical
  hardware 为 `NOT RUN`
- 工作类型：`code_change`
- 源码仓库：
  `https://github.com/m5agent/m5stack-esp-emulator`
- Base commit：
  `a181ac988a24029e94dbcacf5e2a6310e867cfbd`
- Result commit：
  `2175ebbbc94a3de7cd1fc775641e01659cfc2b31`
- 环境：macOS arm64；Python `3.13.15`；Node `v22.14.0`

## 结论

当前状态、未完成工作、历史证据和代码入口已经重新分层：

- `project-status.md` 只保留当前能力、边界、风险和下一门禁；
- `project-backlog.md` 只保留开放 Task、依赖和验收；
- `workstreams.md` 只做工作流路由，不再复制运行流水；
- `validation-ledger.md` 继续保存日期化结果和 evidence；
- `code-map.md` 与五个领域文档契约负责源码、测试和数据入口。

原 6436 行文档契约测试已拆为导航、当前状态、Core2、固件安全、网络/worker
五个模块，旧路径保留兼容入口。141 条退役说法迁入结构化
`stale_doc_claims.json`，由稳定 ID、禁止文本、原因和目录级权威文档路径
驱动检查。

## 关键证据

- 平台测试：`497/497 PASS`
- 文档契约：`37/37 PASS`
- Node 页面 smoke：PASS
- `runtime_coverage`、`peripheral_catalog`、`qemu_profiles`、
  `project_snapshot`：PASS
- `compileall`、selected Ruff `E9/F`、`git diff --check`：PASS
- GitHub Actions `40201058851`：`platform-contracts` 与
  `network-namespace-policy` 两个 job 均 PASS
- `project-status.md`：`803` → `133` 行
- `project-backlog.md`：`412` → `284` 行
- `workstreams.md`：`164` → `84` 行
- 当前最小调查入口明确为 Core2 legacy I2C `RUNTIME-03`

## 文件

- `report.md`：背景、根因、改动、验证和边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：验证摘要与结构指标

## 未覆盖项

- 本次没有重新执行 firmware functional tests、QEMU matrix 或 hardware
  validation；
- Core2 legacy I2C、物理 PSRAM/cache timing、bit-exact controller、物理跨主机
  worker 和真实云端业务边界不变；
- Node 页面 smoke 只证明目录/会话页面接线，不证明固件功能。

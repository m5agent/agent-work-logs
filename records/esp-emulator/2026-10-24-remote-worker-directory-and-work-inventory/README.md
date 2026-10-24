# ESP Emulator 远程 worker 注册目录与工作总整理

- 日期：`2026-10-24`
- 结果：`PASS`（代码、API 契约与文档一致性层）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`a1917eaf410d093d780128696819db7b081b9ae7`
  → follow-up `187a7dc9ad823b449b5a88be6e82d60816c753d7`
- 基线版本：`21d26c93055a65b9952a3d5611838bcbb3f2dc10`
- 环境：macOS Apple Silicon；Python 3；本地 HTTP 契约测试；GitHub Actions

## 结论

把原本尚未提交的远程 worker 持久目录补成可调用、可鉴权、可测试的
`/api/v1/workers` MVP，并将 `project-status`、`project-backlog`、
`workstreams`、代码地图、API 文档和 OpenAPI 统一到同一份事实基线。

当前已具备远程 worker 的 identity/generation 注册、heartbeat、
drain/stop、capability、active lease 清单和有界结果元数据。它仍不是任务
队列、worker supervisor、调度器或活动 QEMU 进程接管实现。

Follow-up 又把代码、当前状态、Backlog、工作流、代码地图、网络/统一运行时文档
和 Core2 native-HCI 证据统一到 `187a7dc`。同时修正 QEMU profile 的陈旧
设备计数，并把 Core2 HLI/API-boundary 诊断更新为可区分 notification
timeout 与 H2C `EIO` 的结构化记录。该诊断 `2/2` 到 NUS subscription 和外部
NUS write，但 notification 仍为 FAIL，完整 GATT 仍属 `OPEN`。

## 关键证据

- 平台测试：`283/283 PASS`；
- 远程目录单元测试：`9/9 PASS`；
- `/api/v1/workers` HTTP 契约及 Bearer token `401/201` 路径：`PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- Follow-up 平台测试：`283/283 PASS`，文档契约 `9/9 PASS`；
- QEMU profile 动态计数：`12` 台 QEMU-backed ESP32 + Tab5 `esp-emu` `PASS`；
- GitHub Actions `40051638039`：`PASS`；
- Core2 HLI/API-boundary 同 build `2/2` 到 NUS write，notification `0/2`，
  属预期 `FAIL` / `OPEN`；失败快照已有一次 H2C `EIO`，先后归因未完成；
- OpenAPI YAML 解析和版本一致性：`1.15.0 PASS`；
- GitHub Actions `40047928762`：`platform-contracts` 与
  `network-namespace-policy` 两个 job 均成功；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：背景、实现、验证、边界和回滚；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：聚合验证结果。
- `evidence/verification.followup.summary.json`：本次代码/文档 follow-up；
- `evidence/core2-hli-api-repeat.summary.json`：Core2 两次重放与失败边界。

## 未覆盖项

- Follow-up 没有修改已提交的 QEMU 控制器、设备数据面或固件运行路径；
- Core2 `--hli-c2h` 依赖 ignored QEMU worktree 中的实验 hook，不能只应用
  已提交的 `0001`/`0002` patch 重放；
- 没有重跑 67-case QEMU 全矩阵，继续引用既有 `67/67`、`274/274` evidence；
- 远程 worker supervisor、持久任务队列、调度和活动 QEMU 进程 re-attach
  仍开放；
- 物理硬件、RF、功耗、声学、光学、机械和电气等价性仍为 `NOT RUN`。

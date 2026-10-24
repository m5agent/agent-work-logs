# ESP Emulator 远程 worker durable job queue

- 日期：`2026-10-24`
- 结果：`PASS`（持久队列、lease supervisor 与 HTTP 契约）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`de5a6c737548c88ade1e318d424da254e3d0778c`
- 结果版本：`22c9564a3c55e543b40d964f4a8ea27e2074073b`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40055533718>
- 环境：macOS Apple Silicon；Python 3；本地 HTTP 契约测试；GitHub Actions

## 结论

`NET-04` 的队列与 lease supervisor 切片已落地。`jobs.json` 持久保存：

- 幂等 job 提交和请求摘要；
- capability requirements；
- queued/leased/completed/failed/cancelled 状态；
- worker identity/generation、lease ID、heartbeat 和 expiry；
- attempts、超时重试、terminal result、cancel 和 failure reason。

`/api/v1/jobs` 已提供 submit/list/get/claim/heartbeat/result/cancel。
worker stale、stopped、missing 或 generation 被替换时，supervisor 会释放
当前 lease；attempts 未耗尽则重新排队，否则失败。状态在服务重启后仍可恢复。

这不是完整 `NET-04`：独立 job executor、evidence bundle 回传、生产多机
调度和活动 QEMU 进程 re-attach 仍为 `NOT RUN`。

## 关键证据

- 平台测试：`289/289 PASS`；
- worker queue：`6/6 PASS`；
- Device Service：`82/82 PASS`；
- HTTP job lifecycle、idempotent replay、claim/lease/result/cancel：`PASS`；
- worker stale/stop/generation 回收和 queue restart recovery：`PASS`；
- GitHub Actions：`Ran 289 tests`、`OK (skipped=2)`，两个 job 均成功；
- runtime coverage、peripheral catalog、QEMU profiles、OpenAPI YAML：
  `PASS`；
- queue 状态文件权限：`0600`；
- 源码 evidence SHA256：
  `0babbd315c7ebff4034eda498a340710716a5a1e8ca0ba34088017902dbbda44`。

## 文件

- `report.md`：状态机、监督规则、验证和回滚；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合结果。

源码证据：
<https://github.com/m5agent/m5stack-esp-emulator/blob/22c9564a3c55e543b40d964f4a8ea27e2074073b/tests/network/worker_queue/evidence-2026-10-24-queue-pass.json>

## 未覆盖项

- 独立 worker executor 和实际 firmware/session 执行；
- evidence bundle 上传、校验和对象存储；
- 活动 QEMU PID/start time 接管或明确 `interrupted_failed`；
- 生产多机容量调度和 warm pool；
- 重复服务/worker 崩溃 soak；
- 物理硬件、RF、功耗、声学和电气验证。

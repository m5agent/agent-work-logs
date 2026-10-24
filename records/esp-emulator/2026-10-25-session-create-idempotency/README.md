# ESP Emulator Idempotent Session Creation

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device session-create scope）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`cd3adc70b815a61f216286250676e0ef7aa8a77d`
- 结果版本：`0e3a913207dd8772d497a8e4dfb5580ba597f5b3`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40142325443>
- 环境：macOS Apple Silicon；真实 Device Service；真实 StickS3 QEMU；WorkerAgent

## 结论

`POST /api/v1/sessions` 现在支持持久化 caller idempotency key。两个并发且
canonical request 相同的 create requests 只产生一个 session、一个 worker
lease 和一个运行中的 QEMU PID；两个响应返回同一 session ID。

行为：

- 同 key + 同请求：返回原 session，`idempotent_replay=true`；
- 同 key + 不同请求：HTTP `409 session_idempotency_conflict`；
- mapping 跨 Device Service restart 保留；
- mapping 文件只保存 SHA256(key)、canonical request SHA256、session ID
  和创建时间；
- raw idempotency key、device ID 或 request body 不写入 mapping；
- mapping mode `0600`。

WorkerAgent 在 job 已 claim 后，以 `job_id + lease_id` 派生稳定 key；service
只返回 session ID 而响应丢失时，worker 的 runtime transient retry 可安全
重发同一 create request。

## 关键证据

- 平台测试：`395/395 PASS`；
- 文档契约：`20/20 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- 真实并发 create：`2` requests；
- session count：`1`；
- 运行中 session PID：存在；
- conflict：HTTP `409`；
- mapping mode：`0600`；
- raw key/device 不在 mapping；
- service restart 后相同请求仍返回原 session；
- WorkerAgent transient create response-loss retry：`PASS`；
- GitHub Actions 两个 job：`PASS`。

源码 evidence：

<https://github.com/m5agent/m5stack-esp-emulator/blob/0e3a913207dd8772d497a8e4dfb5580ba597f5b3/tests/network/session_idempotency/evidence-2026-10-25-session-create-idempotency-pass.json>

## 文件

- `report.md`：设计、执行与边界；
- `run.json`：结构化结果；
- `evidence/verification.summary.json`：脱敏聚合证据。

## 未覆盖项

- 跨主机 idempotency storage；
- 跨 API token 或 tenant 的 key namespace；
- 不提供 key 的 legacy callers 仍不能安全盲目重试 create；
- firmware 完整功能、companion continuity 和真机。

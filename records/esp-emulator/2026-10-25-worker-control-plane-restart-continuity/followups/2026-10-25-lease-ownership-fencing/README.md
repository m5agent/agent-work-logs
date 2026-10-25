# ESP Emulator worker lease ownership fencing

- 日期：`2026-10-25`
- 结果：`PASS`（control-plane contract + worker-local cleanup）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- Base commit：`e914b9f54f7d48c37e41180b29f4c3772100a394`
- 功能提交：`207fe348ecd3d509e6f636fb915cb732b51a946d`
- 心跳回归提交：`8ac85a474e8ad52eb3b4f5836e4344b6e1883c5c`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40155817145>
- 环境：macOS Apple Silicon；真实 `DeviceService` HTTP；Python 3；
  GitHub Actions Ubuntu

## 结论

durable job 的 lease ownership 现在有两侧 fence：

- 队列侧：job 因 lease expiry、worker stale/stop 或 generation 改变而重新
  claim 后，新 claim 得到新的 `lease_id`。旧 lease 的 heartbeat/result
  返回 `409 job_lease_mismatch`，不能覆盖新 claim。
- Worker 侧：`WorkerAgent` 在 job heartbeat 所有权冲突，或有界 transient
  control recovery 用尽后，设置本地 fence，打断 session readiness/evidence
  wait，停止自己可访问的 worker-local runtime session，写
  `lease_fenced=true` 的本地 FAIL result，并拒绝向中央上报 stale result。

该结果关闭 queue result 与 worker 可达本地 runtime 的 stale side-effect
问题。它不能证明物理断网后远端 QEMU/companion 一定停止，也不覆盖外部网络
side effect、物理跨主机迁移或真机。

## 关键证据

- 平台测试：`433/433 PASS`；
- 文档契约：`27/27 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- queue 单测同时拒绝旧 lease heartbeat/result `409`；
- 真实 HTTP 契约验证旧 result `409`、新 result `completed`；
- WorkerAgent 单测验证 heartbeat 409 后 DELETE runtime session、写本地 FAIL，
  且不调用中央 result API；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、OpenAPI YAML、Ruff `E9/F` 和 `git diff --check` 均 PASS；
- CI `40155817145` 的 `platform-contracts` 与
  `network-namespace-policy` 均 PASS。

## 文件

- `report.md`：状态机、实现、验证和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- 物理断网后远端 QEMU/companion 是否真正停止；
- 旧 worker 已经发出的外部网络或宿主 side effect；
- 跨主机进程迁移、跨主机 reattach、跨主机幂等存储；
- NAT/跨子网 worker discovery；
- 生产多机调度和不可信固件 disposable VM；
- physical hardware/RF/power validation。

## Follow-up

- [Network-partition side-effect fencing](followups/2026-10-25-network-partition-side-effect-fencing/)：
  worker→central blackhole 后 bounded heartbeat、runtime DELETE、OS process
  ／真实 QEMU process reap、stale result suppression、lease expiry/requeue
  和 fresh retry PASS；process 与 worker-local QEMU lane 各
  `3/3 × 18 checks`。QEMU 内 guest/device 与 unified companion 仍未覆盖。

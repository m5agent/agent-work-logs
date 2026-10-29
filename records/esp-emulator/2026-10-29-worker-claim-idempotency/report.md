# ESP Emulator worker claim response-loss idempotency 报告

## 背景

`NET-04` 的 durable queue 已支持 submission idempotency、lease fencing 和
worker-side stop/reap，但 claim 没有稳定 request dedup token。若服务端已经
签发 lease 而响应在网络中丢失，WorkerAgent 不能安全盲目重试，因为它可能
领取第二个 job。

## 实现

Device Service API/OpenAPI 升至 `1.49.0`。

1. `POST /api/v1/jobs/claim` 接受可选
   `claim_idempotency_key`，长度 1–160；
2. queue 以 worker identity + claim key 的 SHA256 作为持久索引；
3. request hash 绑定 identity 与可选 `job_id`；
4. 相同 request 且 lease 有效时，返回原 job/lease，
   `claim_idempotent_replay=true`；
5. 相同 key/不同 request 返回 `claim_idempotency_conflict`；
6. lease 过期/撤销或 ownership 改变返回 `claim_idempotency_stale`；
7. 空 no-job poll 不持久化，避免高频空轮询增长；
8. 旧 v1 `jobs.json` 缺少新索引时自动迁移；
9. WorkerAgent 的每个 logical claim 生成新 key，所有 transient retries
   复用该 key，并通过已有 control reconnect/re-register 路径重试。

## 兼容性

claim key 是可选字段；没有 key 的旧 API caller 行为保持不变。旧
`jobs.json` 可加载，新增索引在内存中初始化为空并在下一次写入时持久化。
worker registration、heartbeat、result 和 cancel 契约未改变。

## 失败控制与证据

真实 HTTP fixture 使用内部 control-plane 地址和临时 token；work-log 不保留
该地址或凭据。执行中：

- WorkerAgent 第一次成功读取 claim 后注入 transient loss；
- 第二次 claim 复用同一 key；
- 返回同 job/lease 且 replay flag=true；
- service restart 后直接 replay 仍相同；
- 第二个 job 保持 queued；
- 同 key 改 job 返回 409 conflict；
- 新 key 领取第二个 job；
- queue 文件不含 raw key，mode `0600`；
- service log 不含 token。

11 项 checks 全部 PASS，详细哈希见 `evidence/summary.json`。

## 验证

- 平台：`1529 OK + 1 skipped`；
- worker queue：9 tests PASS；
- worker agent：11 tests PASS；
- Device Service：123 tests PASS；
- OpenAPI inventory、network worker docs、current-state docs：PASS；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、Node contracts 和 `git diff --check`：PASS；
- GitHub Actions
  [`40828778684`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40828778684)
  双 job PASS。

## 边界

该结果证明 central durable queue + same-host WorkerAgent 的
response-loss idempotency，不证明物理跨主机执行、真正网络 blackhole
矩阵、跨主机 queue/session/evidence 存储、QEMU guest/controller 内部状态、
外部 side effect ownership 或 physical hardware。

## 回滚

代码回归可 revert `468eeebc`。API 字段是可选扩展；回滚后旧 caller 不受
影响，但已经写入的 `claim_idempotency` 索引会被旧代码忽略。

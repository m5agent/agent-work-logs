# ESP Emulator Idempotent Session Creation Report

## 背景

Central/runtime restart continuity 已能让 worker 重试已存在的 session，
但 session create 响应丢失时仍可能重复创建 QEMU。Ack 丢失是分布式服务
无法避免的故障，因此 create 必须有稳定 dedup identity。

## 设计

`CreateSessionRequest` 新增 `idempotency_key`：

- key 长度 1–128，禁止控制字符；
- mapping key 为 SHA256(raw key)，raw key 不落盘；
- request identity 为 payload 去除 key 后的 canonical JSON SHA256；
- mapping 保存在 `<state-dir>/session-idempotency.json`，mode `0600`；
- 最多 4096 entries；
- 同 key/hash/session 存在时直接返回原 snapshot；
- 同 key 不同 hash 返回 409；
- mapping 指向的 session 已被 prune 时清除旧 mapping，允许重新创建；
- DeviceService restart 时加载 mapping，配合 session history 返回原 session。

并发 create 在最终 session/lease 分配 lock 内二次检查 mapping，防止两个
请求都越过早期 lookup 后创建两个 session。

WorkerAgent：

- 只有在 job 已 claim 后构造 session；
- 默认 key=`job-<job_id>:<lease_id>`；
- session create 进入 runtime transient retry；
- 若服务已创建但 response 丢失，重试返回原 session；
- 新 job/lease 使用新 key，不复用旧 session。

Claim 本身仍没有稳定 request dedup，因此保持不自动盲重试。

## 执行

真实 fixture：

1. 启动带 token 的真实 Device Service；
2. 两个线程同时 POST 同 key/同 request；
3. 等待唯一 session 进入 running，记录 PID；
4. 同 key/不同 TTL 再 POST，要求 409；
5. 检查 mapping mode、raw key/device 不存在；
6. SIGTERM service；
7. 同 state dir 重启；
8. 再 POST 同 key/request，要求返回原 session。

Unit/contract：

- DeviceService replay、conflict、mapping persistence、0600、raw key redaction；
- WorkerAgent runtime create 先模拟 response loss，再由同 idempotency key
  重试成功；
- WorkerAgent create payload包含 job+lease key。

## 验证

```text
concurrent same key -> one session       PASS
two duplicate responses same session     PASS
one running QEMU PID                     PASS
different request -> 409                 PASS
mapping persisted / 0600                 PASS
raw key/device not persisted             PASS
service restart replay same session      PASS
worker create response-loss retry        PASS
platform tests                           395/395
documentation contracts                  20/20
Node SHA256/upload                       2/2
GitHub Actions                           PASS
```

## 边界

- mapping 是本机 state-dir 文件，不是跨主机数据库；
- 未定义多个 API token/tenant 间的 namespace 隔离；
- 没有 key 的 legacy caller 仍不能安全盲目重试；
- 本记录只证明 session create idempotency，不证明完整固件业务；
- 无 companion continuity 或 physical hardware validation。

## 风险与回滚

主要风险是 key 低熵导致 mapping 可被猜测，但 mapping 仍不保存 raw key 或
请求内容。同 key 异请求和过期 session 都 fail-safe。Rollback
`0e3a913` to `cd3adc7` restores previous non-idempotent create behavior.

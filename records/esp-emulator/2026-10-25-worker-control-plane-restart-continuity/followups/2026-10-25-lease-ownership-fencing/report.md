# ESP Emulator worker lease ownership fencing 报告

## 背景

- 来源：`NET-04` 的 worker 跨主机产品化仍要求外部 side-effect fencing。
- 现象：queue 已经按 worker identity/generation/lease 校验结果，但 worker
  在 heartbeat 发现所有权丢失后仍可能继续等待 evidence，直到执行结束后才
  尝试提交旧结果；期间 worker-local QEMU/companion 仍可产生数据面侧效应。
- 目标：确保 re-claim 后旧 claim 不能覆盖新 claim，并让 WorkerAgent 在
  ownership 无法证明时 fail-closed，尽快停止自己可达的 runtime session。

## 结论

- 状态：`PASS`（queue contract + worker-local cleanup）。
- 关键判断：新 lease ID 是队列 side effect 的 fencing token；
  WorkerAgent 必须在 heartbeat 所有权不再成立时停止本地执行，而不是等
  完整任务结束后再碰运气提交结果。
- 改动范围：`worker_agent.py` 的 execution fence、三个平台测试面、
  Device Service API/OpenAPI `1.32.0`、Backlog/当前状态/证据台账。

## Queue fencing

`WorkerJobQueue` 在 lease expiry、worker stale/stop、missing worker 或
generation replacement 后释放当前 lease。下一次 claim 生成新的随机
`lease_id`。

`heartbeat` 和 `result` 都经过同一个 `_owned_lease()` 校验：

- job 必须仍为 `leased`；
- payload identity 必须匹配；
- payload `lease_id` 必须匹配当前 lease。

因此旧 worker 使用已释放的 lease 会得到 `409 job_lease_mismatch`；即使新
worker 已经 claim 同一 job，旧 worker 也无法覆盖新结果。

## WorkerAgent fencing

`work_once()` 为每次 claim 创建独立 `threading.Event`：

- heartbeat 出现非瞬态 ownership 错误，或在
  `--control-reconnect-timeout` 内无法恢复时，设置 fence；
- session readiness 等待和 evidence delay 使用可被 fence 打断的 wait；
- evidence collection 前后检查 fence；
- `finally` 始终 DELETE 已创建的 runtime session；
- 本地 result 写成 `FAIL`、`lease_fenced=true`；
- fence 已触发时不调用中央 `/jobs/{id}/result`，避免上报 stale terminal
  result；
- `work_once()` 抛出 `WorkerLeaseLostError`，让 worker 当前轮 fail-closed。

该实现没有新增伪造状态或绕过控制器；它只改变 worker 在 ownership 失效时
的生命周期行为。

## 验证

### Queue unit

`test_reclaimed_job_fences_the_previous_lease_result`：

1. claim attempt 1；
2. 将 worker 标为 stale 并 reconcile；
3. claim attempt 2，确认 lease ID 改变；
4. 旧 lease heartbeat 返回 `job_lease_mismatch`；
5. 旧 lease result 返回 `job_lease_mismatch`；
6. 新 lease result 成功，job 为 `completed`。

### Device Service HTTP

通过真实 `ThreadingHTTPServer`：

1. 注册 worker；
2. submit/claim job；
3. 直接以 stale worker snapshot reconcile queue；
4. 第二次 claim 获得新 lease；
5. 旧 result HTTP 请求返回 `409`；
6. 新 result HTTP 请求返回 `completed`。

### WorkerAgent

`test_lease_loss_stops_runtime_and_does_not_report_stale_result`：

- job heartbeat 返回 409；
- evidence delay 被 fence 提前打断；
- runtime session DELETE 被调用；
- 本地 result 为 `FAIL/lease_fenced=true`；
- 中央 result API 调用次数为 0；
- `work_once()` 抛出 `WorkerLeaseLostError`。

### 完整检查

```text
platform tests       433/433 PASS
docs contracts        27/27 PASS
Node tests              2/2 PASS
runtime coverage        PASS
peripheral catalog      PASS
QEMU profiles           PASS
project snapshot        PASS
compileall              PASS
OpenAPI YAML            PASS
Ruff E9/F               PASS
git diff --check        PASS
```

CI run `40155817145` 的两个 job 均 PASS。

## 验证边界

本记录证明：

- central queue 会拒绝旧 lease 的 heartbeat/result；
- WorkerAgent 会停止自己仍能访问的 worker-local runtime session；
- stale result 不会进入 central terminal state。

本记录不证明：

- 控住面断网后，旧 worker 的 QEMU/companion 是否一定收到停止；
- 旧 worker 已经发起的外部请求、OTA、消息或其他不可逆 side effect；
- 进程迁移、跨主机 reattach、跨主机幂等存储；
- 物理硬件、RF、功耗、声学、光学、机械或电气行为。

## 风险与回滚

风险是 worker 因短暂控制面失败提前停止本来仍可完成的任务。当前策略是
fail-closed：只有经过既有 bounded transient recovery 后仍无法证明
ownership 才触发 fence。回滚可 revert `207fe34` 与 `8ac85a4`；不会修改
历史 evidence 或远端任务。

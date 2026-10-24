# ESP Emulator Worker Control-plane Restart Continuity Report

## 背景

Worker 已能把 central control plane 和 worker-local runtime Device Service
分开：central 负责 claim/heartbeat/result，runtime 拥有 QEMU session、
evidence 和 cleanup。此前没有验证 central 重启期间在途 job 是否能收敛。

目标不是迁移 QEMU 进程，而是保持 runtime 不变，验证控制面短暂不可用后：

1. worker 不丢失已 claim lease；
2. identity/generation 不漂移；
3. heartbeat/result 可恢复；
4. terminal job 仍能绑定同一 lease 和 evidence；
5. QEMU/namespace/进程最终清理。

## 实现

WorkerAgent 将 control-plane 请求区分为：

- register：transient failure 可重试；
- 已 claim job 的 worker/job heartbeat：transient network/429/5xx 可重试；
- terminal result：transient failure 可重试；
- claim：不在没有稳定 dedup token 时盲重试，避免响应丢失后重复 claim
  另一份 job。

恢复流程：

```text
control request fails transiently
  -> registered=false
  -> wait/retry within --control-reconnect-timeout
  -> idempotent register same identity/generation
  -> retry original heartbeat/result
```

`WorkerDirectory.register()` 对同一 instance/generation 的重复注册现在同时
刷新 heartbeat 和 stale policy，保持原 active lease IDs，不改变 drain/stop
语义。

`WorkerQueue.result()` 把 originating `lease_id` 写入 terminal result。lease
关闭后仍可把 evidence hash、worker identity 和 claim 关联起来。

OpenAPI 升级到 `1.26.0`，登记 stored result 的 lease and worker identity。

## 初始失败

第一轮真实运行：

- control retry/reconnect：PASS；
- job terminal：FAIL；
- evidence ZIP：不存在；
- QEMU session：failed。

首错：

```text
cannot access local variable 'nic' where it is not associated with a value
```

根因：

- `runtime=qemu` 不创建 qemu-wifi/unified network config；
- launch path 在 network 分支内赋值 `nic`；
- 后续无条件执行 `if nic == "misc.esp32s3.wifi"`；
- 非网络 QEMU 触发 `UnboundLocalError`，session 在 worker 收集 evidence 前失败。

修复：

```text
nic: str | None = None
```

初始化放在 runtime/network 条件分支之前。该修复恢复普通 `runtime=qemu`
worker-local session，不改变 qemu-wifi 或 unified 行为。

失败和成功证据分开保留。

## 最终执行

Fixture：

1. 启动 central 和 runtime 两个真实 Device Service；
2. 提交 `sticks3/runtime=qemu` job；
3. worker 注册并 claim，job=`leased`；
4. 停止 central，保留同一 state dir 和 runtime；
5. worker 继续拥有 runtime/QEMU；
6. 2.2 秒后同端口/state 重启 central；
7. worker 有界发现重连、重注册并重试 heartbeat/result；
8. central 返回 terminal `completed/PASS`；
9. 核对同 identity/generation/lease、evidence ZIP、runtime session 和 QEMU 清理。

结果：

```text
job_claimed_before_restart       PASS
worker_reconnected               PASS
terminal_completed/PASS          PASS
same_lease/identity/generation   PASS
evidence ZIP                     PASS
runtime session stopped          PASS
QEMU process absent              PASS
token absent from worker log     PASS
```

## 验证

```text
platform tests          393/393 PASS
documentation contracts 20/20 PASS
Node SHA256/upload      2/2 PASS
runtime coverage        PASS
peripheral catalog      PASS
QEMU profiles           PASS
project snapshot        PASS
Ruff/compile/diff       PASS
GitHub Actions          PASS
```

CI：

- capability commit `f85b8c9`: run `40141191663`;
- final failure-evidence commit `cd03080`: run `40141285611`.

## 边界

- central control plane only；runtime service 未重启；
- QEMU 没有跨主机迁移；
- claim 响应丢失的 exactly-once 恢复仍开放，因为当前 queue 没有稳定
  claim-request dedup token；
- companion HTTP/BLE/evidence stream 未接管；
- multi-host scheduler、NAT/跨子网 discovery 和 physical hardware 未验证。

## 风险与回滚

风险集中在网络“响应丢失但服务已处理”的请求。register/heartbeat/result
都有 identity/lease 边界；claim 明确不自动盲重试。超出
`--control-reconnect-timeout` 后仍 fail，不制造假 PASS。

Rollback final commit `cd03080` / capability `f85b8c9` to baseline
`658b2d4` restores no control restart retry and no result lease binding.

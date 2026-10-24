# ESP Emulator Worker Runtime-service Restart Continuity Report

## 背景

Central control-plane restart 已证明 worker 可以重新注册并提交原 lease。
下一步是 worker-local runtime Device Service 自身重启：QEMU 进程应继续
运行，新 runtime service 只能在 ownership 全部匹配时重新接管，worker 应
对已存在的 session 继续采集 evidence。

## 设计

WorkerAgent 新增 `--runtime-reconnect-timeout`：

- session create 不在没有 stable create dedup token 时盲重试；
- 已有具体 `session_id` 后，status/evidence/stop 对 transient
  network/429/5xx 做有界重试；
- retry 只作用于 worker-local runtime API，不改 central claim/lease；
- control/runtime 两套重连日志和状态边界分开。

Device Service 继续使用已有 PID + start-time + QMP ownership 算法：

1. 读取 persisted PID；
2. 比较精确 process start-time；
3. 确认 process argv 包含 session-specific QMP path；
4. 连接 QMP；
5. `query-status` 必须为 running；
6. 才设置 `reattached_process=true`。

任何不匹配都应恢复为 interrupted failed，而不是按 PID 直接接管。

## 执行

1. 启动 central 和 runtime 两个真实 Device Service；
2. worker 注册并 claim `sticks3/runtime=qemu` job；
3. runtime 启动真实 QEMU，等待 state running；
4. 记录 session ID、PID 和 process ownership；
5. 只对 runtime service 发 SIGKILL；
6. QEMU 继续运行，runtime downtime `2.2s`；
7. 同 port/state 启动新 runtime service；
8. 新服务 reattach 同一 session/PID；
9. worker status/evidence retry 成功；
10. central terminal result `completed/PASS`；
11. 核对 evidence ZIP 和 cleanup。

## 验证

```text
same runtime session             PASS
same QEMU PID                    PASS
start-time/QMP ownership         PASS
reattached_process               PASS
worker runtime retry/reconnect   PASS
terminal completed/PASS          PASS
same lease/worker identity       PASS
evidence manifest + serial       PASS
session stopped / PID released   PASS
QEMU process reaped              PASS
```

```text
platform tests          394/394 PASS
documentation contracts 20/20 PASS
Node SHA256/upload      2/2 PASS
runtime/catalog/profile/snapshot PASS
Ruff/compile/diff       PASS
GitHub Actions          PASS
```

## 边界

- runtime restart 和 reattach 在同主机完成；
- QEMU 没有跨主机迁移；
- session create 失败后没有自动 dedup 恢复；
- companion HTTP/BLE helper、Tab5/network lane 和 evidence stream 更完整
  连续性未覆盖；
- 无物理硬件验证。

## 风险与回滚

风险集中在“旧 runtime 已处理但响应丢失”的 create/stop 请求。当前只重试
已有 session ID 的幂等 status/evidence/stop；create 保持 fail-closed。
Rollback `cd3adc70` to `cd030802` removes runtime retry and restart evidence
continuity.

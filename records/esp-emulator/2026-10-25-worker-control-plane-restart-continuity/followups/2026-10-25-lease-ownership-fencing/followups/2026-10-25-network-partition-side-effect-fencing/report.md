# Worker Network-Partition Side-Effect Fencing Report

## 背景

已有 `409 job_lease_mismatch` 证据证明：队列 re-claim 后，旧 lease 的
heartbeat/result 不能覆盖新 claim；WorkerAgent 也会删除其可达 runtime
session。

但网络 blackhole 与显式 `409` 不同：请求可能保持 TCP 连接但永远收不到响应。
原实现只在异常返回后检查 reconnect deadline；首次 HTTP 请求仍可使用默认
60 秒 timeout。这样 `control-reconnect-timeout=1s` 的网络分区可能被拖到
一分钟，期间本地 runtime side effect 继续运行。

## 根因与修复

### 根因

`_control_recovery()` 维护总 deadline，但调用 `Api.json(timeout=60)` 时没有
把剩余 recovery budget 传给当前请求。故障只有在 socket layer 自己返回后
才被分类，因此 blackhole 下 fence 不及时。

### 修复

- `_control_recovery()` 的 operation 接收当前 request timeout；
- 每次 registration/heartbeat/result 请求使用
  `min(original_timeout, remaining_recovery_budget)`；
- registration 与后续 operation 共用同一个 deadline；
- deadline 前未恢复时返回 transient error，heartbeat loop 设置 lease fence；
- 新增 `M5_JOB_LEASE_SECONDS` 环境变量，允许有界配置 remote job lease，
  默认仍为 60 秒，范围 clamp 到 5–3600 秒；
- 新增真实 namespace fixture 和 transparent timeout 单测。

## 测试拓扑

```text
server namespace              worker namespace
10.214.0.1/24        <->      10.214.0.2/24
central Device Service        WorkerAgent
durable job queue             authenticated runtime fixture
                              child process side effect
```

分区规则只丢弃 worker→central 的 control TCP。Worker-local loopback
runtime 仍可达，因此 worker 有能力执行 DELETE/cleanup。

## 执行

每次 attempt：

1. 启动 central Device Service，job lease 配置为 5 秒；
2. 启动 runtime fixture；
3. 提交带 `evidence_delay_seconds=8` 的 job；
4. attempt 1 claim job、创建 runtime session 和 child process；
5. 确认 child PID alive 后安装 worker→central nftables drop；
6. heartbeat request 在剩余 budget 内 timeout；
7. worker fence，DELETE runtime session，terminate/wait child；
8. worker 不提交 stale result，本地 result 为 FAIL/`lease_fenced=true`；
9. 观察 central job 仍为 attempt 1/leased，然后恢复网络；
10. central lease 到期并重排；
11. attempt 2 claim，runtime 完成 evidence ZIP，terminal result PASS；
12. 第二个 runtime session/process 也被正常停止和回收。

## 验证

三个独立运行：

```text
attempts                         3/3 PASS
checks per attempt               18/18 PASS
job attempts                     2
attempt 1 worker returncode      1
attempt 1 lease_fenced           true
attempt 1 process reaped         true
attempt 2 worker returncode      0
attempt 2 result                 PASS
attempt 2 process reaped         true
namespaces/service cleanup       PASS
tool hashes unchanged            true
```

平台验证：

```text
platform unittest        444/444 PASS
docs consistency         30/30 PASS
Node SHA256/upload       2/2 PASS
runtime coverage         PASS
peripheral catalog       PASS
QEMU profiles            PASS
project snapshot         PASS
Ruff fatal checks        PASS
compileall               PASS
OpenAPI / CI YAML        PASS
git diff check           PASS
GitHub Actions           PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40160702972>

## 验证边界

- runtime fixture 是 authenticated HTTP session + OS child process，不是 QEMU；
- 证明 worker-owned process side effect，不证明 QEMU/device/controller
  side effect 或 worker 未拥有的外部网络 side effect；
- 两个 namespace 位于同一 Docker daemon，不是物理跨主机；
- 不证明跨主机进程迁移、reattach、生产 scheduler 或 hardware；
- control-plane authenticity、TLS/mTLS 和 worker HMAC 仍由既有路径负责。

## 风险与回滚

- 缩短 request timeout 会让 control-plane 短暂拥塞更快暴露为 fence；
  heartbeat/claim 属于短请求，当前契约不接受长时间阻塞。
- lease 至少 5 秒，避免测试或运维误配为不可恢复的零窗口。
- 本地 fence 会在无法确认 ownership 时保守停止 runtime；central 仍可能暂时
  将此 job 视为 leased，直到 lease expiry。
- 回滚为 revert `fa902c2`，恢复旧请求 timeout 行为并移除 partition fixture；
  不影响已有 `409` fencing。

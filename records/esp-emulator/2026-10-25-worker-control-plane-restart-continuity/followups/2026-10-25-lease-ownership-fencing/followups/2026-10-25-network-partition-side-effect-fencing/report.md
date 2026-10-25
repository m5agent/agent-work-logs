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
<control-fixture-subnet> <-> <worker-fixture-subnet>
central Device Service        WorkerAgent
durable job queue             authenticated runtime fixture
                              child process side effect
```

分区规则只丢弃 worker→central 的 control TCP。Worker-local loopback
runtime 仍可达，因此 worker 有能力执行 DELETE/cleanup。

真实 QEMU mode 使用相同 namespace 和 control-plane 规则，但 worker
namespace 内运行独立 Device Service：

```text
central Device Service        worker-local Device Service
durable queue/directory   <-> authenticated runtime API
                              full StickS3 flash upload
                              qemu-system-xtensa + session evidence
```

该 mode 的 side effect 是 worker-owned QEMU process，不是 child-process
fixture。

最终 runner 还支持同一 lease 的 `qemu-unified`：

```text
worker-local Device Service
  ├─ qemu-system-xtensa
  ├─ in-process HTTP fixture
  ├─ external BLE peer + UART1 H4
  └─ QEMU pcap
```

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

QEMU mode 重复同样的 attempt 1 fence/requeue/attempt 2 流程，并额外要求：

1. worker 上传完整源固件并生成 normalized artifact；
2. attempt 1 启动真实 `qemu-system-xtensa`；
3. partition 后 device session stop，QEMU PID 消失；
4. attempt 2 启动新的 QEMU，不再复活 attempt 1；
5. attempt 2 取得 serial/frame/QOM evidence，terminal result PASS；
6. 两代 QEMU 和 namespace 都回收，stale result 不上报。

Unified mode 在 partition 前额外要求同一 session 产生 HTTP request、BLE
`BLE_BUMBLE_PASS` 和非空 pcap。Partition 后要求 HTTP/BLE companion 变成
`terminated`、BLE peer PID 消失、pcap summary 完成；attempt 2 再启动新
unified session 并重复全部 HTTP/BLE/pcap evidence。

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

真实 QEMU lane 同样为 `3/3 PASS`、每轮 `18/18` checks：

```text
attempt 1 QEMU started                    PASS
attempt 1 lease fenced                    PASS
attempt 1 QEMU PID reaped                 PASS
attempt 2 fresh QEMU started              PASS
attempt 2 evidence + terminal result      PASS
input firmware/runtime hashes unchanged   true
```

最终 runner 的三条 lane 均在干净 source worktree 上重新执行：

```text
process lane                 3/3 PASS x 18 checks
plain QEMU lane              3/3 PASS x 18 checks
qemu-unified lane            3/3 PASS x 30 checks
source revision              d846c4b
runner hash                  d5f572f...
unified HTTP before fence    1 request
unified BLE before fence     PASS
unified pcap before fence    8249 B
unified companion after      terminated
unified BLE PID after        reaped
unified pcap summary         PASS
retry unified HTTP/BLE/pcap  PASS
```

平台验证：

```text
platform unittest        447/447 PASS
docs consistency         33/33 PASS
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
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40163740320>

## 验证边界

- runtime fixture 是 authenticated HTTP session + OS child process，不是 QEMU；
- process lane 证明 worker-owned child process；QEMU lane进一步证明
  worker-local QEMU **process** 被 stop/reap；
- 不证明 QEMU 内 guest/device/controller-internal side effect；
- unified lane 证明 provider 管理的 HTTP/BLE/pcap 随 runtime 停止，但不观察
  QEMU 退出后的 guest/controller 内部状态；
- 不证明 worker 未拥有的外部网络 side effect；
- 两个 namespace 位于同一 Docker daemon，不是物理跨主机；
- 不证明跨主机进程迁移、reattach、生产 scheduler 或 hardware；
- control-plane authenticity、TLS/mTLS 和 worker HMAC 仍由既有路径负责。

## 风险与回滚

- 缩短 request timeout 会让 control-plane 短暂拥塞更快暴露为 fence；
  heartbeat/claim 属于短请求，当前契约不接受长时间阻塞。
- lease 至少 5 秒，避免测试或运维误配为不可恢复的零窗口。
- 本地 fence 会在无法确认 ownership 时保守停止 runtime；central 仍可能暂时
  将此 job 视为 leased，直到 lease expiry。
- 回滚 process/QEMU/unified lane 为 revert `6866fbd`、`d846c4b` 和
  `ff60575`；回滚请求 timeout 修复为
  revert `fa902c2`。`fa902c2` 的核心 bounded-budget 行为不应单独撤销，
  否则 blackhole 会重新被默认 60 秒 socket timeout 拖住。

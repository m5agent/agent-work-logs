# Cross-network-namespace worker control plane 报告

## 背景

现有 worker queue、HMAC、TLS/mTLS、generation-pointer migration 和真实
QEMU executor 证据主要来自同主机 loopback。`NET-04` 仍无法声称 control
plane 能跨主机边界工作。为了在不影响 Core2 soak、也不搭建第二台物理主机
的情况下先缩小这个缺口，新增了两个独立 network namespace 的 Linux fixture。

## 拓扑

```text
server namespace                          worker namespace
real Device Service  <--- veth /30 --->  real WorkerAgent client
        |                                        |
        +-- durable jobs, workers, leases        +-- registration
        +-- authorization + HMAC verification    +-- submit / claim
                                                 +-- heartbeats
                                                 +-- terminal result
```

fixture 使用私有 veth 地址，并在 Linux container / GitHub runner 中运行。

## 执行流程

1. 创建 server/worker 两个 network namespace 和 veth peer；
2. 给两端分配同网段 /30 地址并启用接口；
3. 在 server namespace 启动真实 `serve.py`；
4. 在 worker namespace 启动真实 `WorkerAgent` client；
5. client 使用 authorization header + worker/generation HMAC 注册；
6. 提交只要求 `network_namespace` 和 `control_plane_only` capability 的
   transport-only job；
7. claim job，发送 worker heartbeat 和 job lease heartbeat；
8. 提交带 bounded summary/SHA256 的 terminal PASS；
9. 查询 terminal completed 并 stop worker；
10. 停止 server、删除两个 namespace，并验证 API credential 不在日志中。

## 结果

所有 checks PASS：

- worker exit 0；
- server 在测试时存活并在结束时终止；
- worker route 经过预期 veth；
- worker registration 记录；
- job submitted 与 claimed；
- worker/job heartbeat；
- terminal completed；
- worker stopped；
- `qemu_started=false`；
- `device_session_created=false`；
- namespaces cleaned；
- API credential not logged。

本地 privileged Linux container 和 GitHub Actions 同一 source commit 均
成功。原始 worker/job/lease/instance 标识、临时网络名字和日志路径不出现在
公开摘要中。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compileall 和平台契约 |
| transport | `PASS` | 真实 server/worker namespace、veth route 和 HTTP |
| device_response | `PASS` | registration 201、claim/heartbeat/result 200 |
| data_behavior | `PASS` | capability match、terminal state 和 cleanup |
| visual_or_physical | `NOT RUN` | 不涉及 UI、QEMU 或硬件 |
| delivery | `PASS` | source commit 和 CI 已推送 |

## 验证边界

- 这不是 cross-host QEMU executor；
- 没有 companion HTTP/BLE 或 evidence stream；
- 没有跨主机 process re-attach；
- 没有生产多机 scheduler；
- 没有物理硬件、RF 或电气验证。

## 风险与回滚

fixture 只在两个临时 namespace 内创建 veth 和服务进程，正常与失败路径都
删除 namespace。回滚 commit：
`ad6e96e69757eafd13993f0d45484c42d4476182`。

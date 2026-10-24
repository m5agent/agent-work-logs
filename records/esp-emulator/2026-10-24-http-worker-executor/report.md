# HTTP-only worker executor 报告

## 背景

durable queue 已完成 claim/lease/result，本地 QEMU restart reattach 也已
完成，但还没有独立进程真正消费 job。此前的 queue 只能证明状态机，不能
证明 job 能产生真实设备 session 和 evidence。

本轮实现同主机 HTTP executor，作为远程 worker 的可执行基线。

## 实现

`platform/tools/worker_agent.py`：

- `agent-state.json` 持久化 worker identity；同一 work-dir 重启 generation +1；
- `POST /workers` 注册，按 heartbeat interval 更新 worker lease 列表；
- `POST /jobs/claim` claim 最老兼容 job；
- 后台线程同时 heartbeat job lease 和 worker directory；
- `POST /sessions` 创建 job 指定的 session；
- 轮询 session 直到 `running` 或 terminal；
- `GET /sessions/{id}/evidence` 下载 ZIP，校验 ZIP magic 和 SHA256；
- `DELETE /sessions/{id}?purge=0` 保留历史；
- `POST /jobs/{id}/result` 回报 terminal state、evidence hash 和 bounded summary；
- 本地以 `0600` 保存 evidence ZIP 和 result JSON；
- 干净退出调用 `/workers/{id}/stop`。

agent 不导入 Device Service 内部模块，不直接起 QEMU，不读写服务状态目录，
也不包含任何 firmware/session-specific 捷径。

## 执行

真实 live job：

```text
submit durable job            201
worker register               201
claim                         200, leased
session create                202
session poll -> running       PASS
job/worker heartbeat          PASS
evidence ZIP                  6891 bytes
evidence SHA256               fda2344f...
session stop purge=0          200
job result                    200, completed/PASS
worker stop                   200
agent exit                    0
```

本地：

```text
platform tests                 292/292 PASS
worker agent tests             3/3 PASS
live executor                  1/1 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
Ruff / py_compile              PASS
git diff --check               PASS
```

GitHub Actions `40056513345`：

```text
platform-contracts       success
network-namespace-policy success
Ran 292 tests
OK (skipped=2)
```

## 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile 与平台测试 |
| transport | `PASS` | HTTP-only worker/job/session/evidence API |
| device_response | `PASS` | 真实 StickS3 QEMU session 到达 running |
| data_behavior | `PASS` | claim、lease heartbeat、evidence hash、stop 和 job result |
| visual_or_physical | `NOT RUN` | 未采集 UI 或物理测量 |
| review/delivery | `PASS` | 文档、OpenAPI 兼容性、CI 与归档 |

## 边界

- live 测试在同一 host，不等于跨主机 worker 网络和 auth；
- 没有 worker authentication、authorization、mTLS 或 lease fencing 强化；
- session `running` 是控制面状态，不代表应用 UI/功能通过；
- service 重启后 companion HTTP/BLE/evidence continuity 仍未实现；
- 不是生产 scheduler、warm pool、恶意固件沙箱或真机验证。

## 风险与回滚

executor 可能重复执行 lease 超时后的同一 job；queue 的 generation/lease
ownership 会拒绝旧 lease 提交，但外部 side effect 仍需 future idempotency
fencing。

回滚源码提交
`d200bada9e72593db21cdfb191cdb59e488439a4` 会移除 worker agent 和文档
更新，不影响 queue、Device Service API、QEMU worktree、firmware 或历史
session。

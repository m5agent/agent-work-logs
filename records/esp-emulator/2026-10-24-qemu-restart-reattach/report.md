# 本地 QEMU restart re-attach 报告

## 背景

服务重启前会把 persisted active session 全部恢复为 interrupted failed。
这避免了假 `running`，但会让仍然存活、QMP 仍可控制的 QEMU 变成不可继续的
历史记录，并可能留下孤儿进程。

本轮实现 `SVC-01` 的本地控制面切片：只有进程 ownership 能被强证据证明时
才接管，否则继续 fail closed。

## Ownership 设计

仅保存和比较 PID 不够：PID 可能被复用。最终门禁要求：

1. session record 中有正整数 PID 和 start-time token；
2. 当前 `ps -ww -p PID -o lstart=` 与记录完全一致；
3. 当前 `ps -ww -p PID -o command=` 包含
   `/tmp/m5-service-<session_id>.sock`；
4. QMP socket 能连接；
5. `query-status` 为 `running`；
6. 新 Device Service generation 能 reserve 新的本地 worker lease。

失败时 `mark_interrupted()` 写入 failed、错误原因和 `interrupted` event。
成功时写入 `reattached` event。

## 改动

- session JSON 持久化 `process_start_token`、`worker_lease_active` 和
  `reattached_process`；
- QEMU launch 后立即记录 PID start-time；
- restore 时只尝试本地 QEMU/QMP runtime；
- reattach 成功后将 worker generation 更新为新进程 generation；
- janitor 和 snapshot 会检测 reattached process 消失或 identity 变化；
- stop 只会在 start-time/QMP ownership 仍匹配时发送 TERM/KILL，避免误杀
  PID reuse；
- OpenAPI 增加 `reattached_process` 和 `recovery_scope`；
- 文档明确只恢复 QEMU/QMP control plane。

## 验证

本地：

```text
platform tests                 289/289 PASS
Device Service                 82/82 PASS
targeted reattach               1/1 PASS
live service restart            1/1 PASS
runtime coverage                PASS
peripheral catalog              PASS
QEMU profiles                   PASS
OpenAPI YAML                    PASS
Ruff / py_compile               PASS
git diff --check                PASS
```

live 流程：

```text
start service A
create real sticks3 QEMU session -> running
SIGKILL service A PID only
QEMU remains alive
start service B with same state directory
session B -> running, same QEMU PID
reattached_process=true
recovery_scope=qemu-control-plane
worker generation=2
stop -> QEMU exits
```

GitHub Actions `40056119661`：

```text
platform-contracts        success
network-namespace-policy  success
Ran 289 tests
OK (skipped=2)
```

## 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile 与平台测试 |
| transport | `PASS` | 真实 QMP 连接、query-status 和设备 stop |
| device_response | `PASS` | 真实 StickS3 QEMU 在服务崩溃后继续运行 |
| data_behavior | `PASS` | PID/start-time/ownership 校验、worker gen 2 lease 和 cleanup |
| visual_or_physical | `NOT RUN` | 本轮未采集 UI 或物理测量 |
| review/delivery | `PASS` | OpenAPI、文档、CI 和归档 |

## 边界

- 只证明本地 QEMU/QMP control plane；
- companion HTTP fixture、BLE probe、native VHCI/GDB helper、pcap writer 和
  evidence stream 可能随旧服务消失，不能从 reattach PASS 推导完整恢复；
- Tab5/network lane 没有可重连 QMP，仍为 interrupted history；
- paused QEMU 不会接管；
- 跨主机和多租户 API 不在本轮；
- 不是固件、RF 或硬件验证。

## 风险与回滚

如果 start-time 或 QMP ownership 判断有误，代码选择拒绝接管，不会误杀
其他 PID。回滚源码提交
`b31c3ab6d827b7e2a7199e3e30e75952fe4eaa20` 会恢复旧的
interrupted-failed 行为，不修改 QEMU worktree、firmware 或历史 evidence。

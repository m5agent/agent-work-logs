# ESP Emulator Local Worker Lifecycle 报告

## 背景

Device Service 已支持 lease、停止/失败历史、最后一帧和存储 GC，但 worker
本身没有持久身份、heartbeat、drain 或重启分类。服务重启时，旧活动会话只会
统一恢复为 interrupted failed，无法从 worker 侧看出旧进程是否曾持有 lease；
第二个服务进程也可能误用同一状态目录。

本阶段目标是建立本地 worker 生命周期控制，同时保持以下边界：

- 一个 live service 进程独占一个 worker 状态目录；
- drain 只停止新 lease admission，不强制杀死活动会话；
- heartbeat 和 lease 是持久化证据，不是远程 scheduler；
- 进程重启若不能 re-attach，就必须明确记录 abandoned lease 和 interrupted
  session，不能假装继续运行。

## 实现

新增 `platform/tools/worker_registry.py`：

- stable `worker_id`、per-process `instance_id`、递增 `generation`；
- `flock` 独占 `<state>.lock`；
- atomic `worker.json`，包含 heartbeat、active leases、abandoned leases 和
  bounded recent results；
- `ready → draining → drained` 与 `resume` 状态转换；
- stale heartbeat 时拒绝新 lease；
- 新 worker generation 启动时把上一代 active leases 转为 abandoned。

Device Service 集成：

- session 创建前预留 worker lease，失败/停止时幂等释放；
- session record/snapshot/event timeline 记录 worker ID、generation 和 lease；
- worker result 记录 device、runtime、firmware SHA、session state、
  network status、pcap availability 和 evidence availability；
- capacity 和 health 返回精简 worker snapshot；
- `GET /worker`、`POST /worker/drain`、`POST /worker/resume`；
- API contract 升级为 `1.14.0`。

## 执行

`tests/network/worker_lifecycle/run_test.py` 使用真实本地服务：

1. 通过正式 Artifact/Firmware API 将缓存 StickS3 参考镜像补齐为完整 8 MiB；
2. 创建 `qemu-wifi` lease，等待 running 和可读 framebuffer；
3. 验证 heartbeat、稳定 worker ID 和 active lease；
4. drain 后拒绝新 lease，同时原会话继续运行；
5. 停止原会话，验证 worker 进入 `drained` 且 recent result 保留 pcap；
6. resume 后创建第二个会话；
7. SIGKILL 服务进程组，确认所有 QEMU 子进程消失；
8. 用同一状态目录启动 generation 2；
9. 验证 abandoned lease、interrupted failed session 和 active lease 归零。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | compileall、平台测试和 CI |
| service API | PASS | worker endpoints、capacity、session worker metadata |
| lease lifecycle | PASS | reserve、drain、release、resume、recent result |
| restart classification | PASS | generation 2、abandoned lease、interrupted session |
| QEMU runtime | PASS | 真实 StickS3 `qemu-wifi` session、frame 和进程组清理 |
| pcap retention | PARTIAL | worker result 记录 pcap availability；同轮 network evidence 为 `PARTIAL`，不是网络功能 PASS |
| full platform suite | PASS | `264/264` |
| GitHub Actions | PASS | run `40037664731` |
| remote worker / re-attach | NOT RUN | 本阶段只实现本地 lifecycle |
| physical hardware | NOT RUN | 未执行真机 |

固定结果：

- worker generation：`1 → 2`
- 强杀后 abandoned lease：`1`
- 重启后 active lease：`0`
- 完整 reference firmware SHA256：
  `a5d027f6d2953edb9ece45cddea1490112d8e421ba563edc6e7c71cf7ac4f6ec`
- 初始 framebuffer SHA256：
  `72bf95e3ae18e1b43989b18caff8c4b73e2cd33d41cb0599ba744e520ce5cd8f`

## 验证边界

- 这是本地 trusted-host worker control，不是恶意固件 sandbox；
- SIGKILL 验证说明下一代会明确失败收敛，不代表运行中的 QEMU 已支持
  re-attach；
- pcap availability 只证明文件被记录，network evidence 仍为 `PARTIAL`；
- 没有远程 coordinator、队列、租约迁移、warm pool 或多主机调度；
- 没有物理硬件、RF、功耗或长期稳定性结论。

## 风险与回滚

worker 状态目录是单 writer：第二个 live worker 会返回
`worker_state_locked`，必须显式停止旧实例或更换状态目录。drain 不设置硬
deadline，仍需由 scheduler/operator 后续停止活动会话。

回滚源码提交 `689c49b77ff6595a97dc57d3b3e6b37bef7fde8d` 会移除本地 worker
registry、API、lifecycle fixture 和对应文档；不会删除已有 session history。

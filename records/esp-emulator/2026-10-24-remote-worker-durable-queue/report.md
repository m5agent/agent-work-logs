# 远程 worker durable job queue 报告

## 背景

远程 worker 注册目录已经具备 identity/generation、heartbeat、drain/stop、
capability 和 bounded result metadata，但 Device Service 仍不能持久保存
远程任务，也不能在 worker 失联后给出确定的 lease 收敛结果。

本轮目标只覆盖 `NET-04` 的队列与 supervisor 层：

- 幂等接收 job；
- 按 capability 分配给 ready worker；
- 给 worker 有期限、可续期的 lease；
- lease 超时或 worker 状态变化时重试或失败；
- 保存 terminal result 并允许 operator cancel；
- 服务重启后恢复状态。

不把 claimed job 冒充为已经执行，也不接管活动 QEMU。

## 实现

新增 `platform/tools/worker_queue.py`：

- `jobs.json` 原子写入并设置 `0600`；
- 最多 `1024` jobs、请求 `64 KiB`、summary `8 KiB`、最多 `10` attempts；
- 默认 lease `60s`，heartbeat 只能由同一
  `worker_id/instance_id/generation/lease_id` 续期；
- `idempotency_key` 绑定 canonical request digest，不同请求复用同一 key
  返回 `409`；
- 队列按 FIFO 选择最老兼容 job；
- worker stale/stopped/missing/generation replacement 时释放 lease；
- attempts 未耗尽则回到 queued，否则 failed；
- PASS/PARTIAL/REVIEW 记 completed，FAIL 记 failed；
- terminal result 可带 lowercase SHA256 和 bounded summary；
- 队列容量达到上限时先清理最老 terminal jobs。

Device Service：

- 初始化 `state-dir/jobs.json`；
- janitor 每 2 秒将 worker directory 快照交给 queue supervisor；
- 暴露 `/api/v1/jobs`、`/jobs/claim`、heartbeat、result、cancel；
- OpenAPI 升级到 `1.17.0` 并加入 job schemas。

## 验证

本地：

```text
platform tests         289/289 PASS
worker queue tests     6/6 PASS
Device Service tests   82/82 PASS
runtime coverage       PASS
peripheral catalog     PASS
QEMU profiles          PASS
OpenAPI YAML           PASS
Ruff / py_compile      PASS
git diff --check       PASS
```

HTTP 契约覆盖：

```text
POST /jobs                    201
POST /jobs (idempotent replay) 201, same job_id
POST /jobs/claim              200, leased
POST /jobs/{id}/heartbeat     200, lease renewed
POST /jobs/{id}/result        200, completed
GET  /jobs?status=completed   200
POST /jobs/{id}/cancel        200, cancelled
```

GitHub Actions `40055533718`：

```text
platform-contracts       success
network-namespace-policy success
Ran 289 tests
OK (skipped=2)
```

## 验证层级

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | Python compile 与平台测试导入 |
| transport | `PASS` | 本地 HTTP `/api/v1/jobs` 契约 |
| device_response | `NOT RUN` | 本轮不执行设备 job |
| data_behavior | `PASS` | queue 状态、lease、retry、supervisor 与持久恢复 |
| visual_or_physical | `NOT RUN` | 没有物理设备测量 |
| review/delivery | `PASS` | OpenAPI、文档、CI 和工作记录 |

## 边界

- claim 成功不代表 worker 已执行 firmware 或产生 evidence；
- 没有独立 executor、evidence bundle 回传和活动 QEMU re-attach；
- 没有生产多机容量调度、quota、warm pool 或跨 worker 公平性；
- JSON 状态依赖 Device Service 的单实例 state-directory lock；
- 不是恶意固件沙箱，也没有真机、RF、功耗或电气结论。

## 风险与回滚

回滚源码提交
`22c9564a3c55e543b40d964f4a8ea27e2074073b` 会移除 queue、API、测试和
文档更新，不会修改 QEMU worktree、firmware、历史 session 或 evidence。
`jobs.json` 是新增状态文件，测试和仓库未包含真实任务数据。

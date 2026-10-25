# Worker QEMU across Docker containers report

## 背景

已有 worker-local QEMU 证明 central 与 runtime 分属同一主机上的两个 network
namespace，但尚不能证明控制与执行边界跨独立容器网络。下一步使用两个
Docker 容器和 user-defined bridge，在不冒充物理跨主机的前提下推进
`NET-04`。

## 结论

该跨容器门禁通过。central 容器和 worker 容器拥有不同的 container ID 与
network namespace，只通过 bridge 上的容器 DNS/服务端口通信。

worker 容器中：

1. `worker_agent` 从 central 注册并 claim durable job；
2. worker 内独立 Device Service 上传/规范化 firmware；
3. runtime 启动真实 StickS3 QEMU session；
4. evidence ZIP 包含 manifest、serial、QEMU logs 和 QOM snapshot；
5. result 回报 central，terminal 为 `completed/PASS`。

运行完成后 QEMU、worker/central 容器和 bridge 全部清理。

## 诊断与修复

第一次运行：

- central 容器正常启动；
- worker 无法访问容器网络名；
- 根因是继承/注入的代理环境改变了容器间 HTTP 路由；
- 修复：central/worker 双方显式清空大小写 proxy 变量，并设置
  `NO_PROXY=*`/`no_proxy=*`。

第二次运行：

- worker 已注册，runtime plane 已识别，firmware 已上传；
- session 在 QEMU 前失败并返回 `backend_not_ready`；
- 根因是 runner 把宿主绝对 QEMU/ROM 路径写进容器环境；
- 修复：统一转换为 `/workspace/...` 容器挂载路径。

第三次运行完成全链路，但为增强复现性，最终 Dockerfile pin 了 Ubuntu
25.04 image digest，并重新执行三次当前实现运行。

## 改动

- 新增 `worker_cross_container` Dockerfile、runner、summarizer、README 和
  evidence；
- 复用 `worker_cross_netns --qemu-worker` 作为 worker 内协议入口；
- 容器之间检查 control API 可达、worker 注册、terminal result、runtime
  plane、QEMU/session、三个 artifact hash、evidence、token redaction、
  QEMU reap、container/network cleanup；
- 更新当前状态、Backlog、workstreams、code map、网络方案、验证台账和自动
  snapshot。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | pinned Docker image、compileall、OpenAPI、docs contracts |
| transport | `PASS` | central/worker 跨 Docker bridge 注册、claim、heartbeat、result |
| device_response | `PASS` | worker-local Device Service 创建真实 QEMU session |
| data_behavior | `PASS` | terminal PASS、manifest/serial/QOM evidence、三哈希 |
| cleanup | `PASS` | QEMU reap、container cleanup、bridge cleanup |
| visual_or_physical | `NOT RUN` | 无 RF、功耗、电气或物理硬件测试 |
| delivery | `PASS` | source commit + CI `40154787407` |

## 验证边界

这是两个独立容器共享 one Docker daemon 的 `virtual-device validation`。
它不证明物理独立主机、WAN/NAT、跨子网 discovery、跨主机迁移/re-attach、
companion continuity、生产调度或 hardware validation。

## 风险与回滚

本轮只运行临时容器和用户桥；未执行物理烧录或持久服务变更。回滚 result
commit 可移除 fixture 和文档状态，不影响已有 queue/runtime 契约。

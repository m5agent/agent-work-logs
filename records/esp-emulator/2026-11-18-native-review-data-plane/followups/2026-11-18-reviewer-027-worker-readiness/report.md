# Reviewer 候选与真实 Device Service 对照

## 环境

使用 Reviewer 候选 `a2d468b989139450ab95929597622bfa2074b7c3` 与 Device Service 1.99.0 `a729e24b1e4724b783ab2d59eec689cfdfeb24b3`。两者以独立状态目录和隔离测试配置启动。Reviewer 使用经认证的实际 Device Service worker 状态。源代码和 OpenAPI 哈希随 [结构化回执](evidence/readiness.summary.json) 保留。

## 验收步骤

先运行 Reviewer 候选并保留 Device 停机状态。随后启动 Device，暂停接收新租约，再恢复接收。每步读取 Reviewer 就绪结果并核对实际 Device worker 状态，每步核对响应携带的 OpenAPI 版本。Device 首次启动前和最后再次停止后，均确认 Reviewer 旧健康检查仍可回应。

| Device 状态 | Reviewer 就绪 HTTP | 实测原因 |
| --- | --- | --- |
| 不可达 | 503 | `worker_unavailable` |
| 接收租约 | 200 | 就绪 |
| 暂停接收租约 | 503 | `worker_not_accepting_leases` |
| 恢复接收租约 | 200 | 就绪 |

旧健康检查继续可用，OpenAPI 0.27.0 哈希固定。候选 295 项单测通过，YAML 合约检查通过。结束前活动租约为零，所启动的进程全部退出。

## 边界

本次验收覆盖 API 就绪检查。同一提交已进入 Reviewer 源码主分支。该版本的原版固件干跑和常驻部署均为 `NOT RUN`。Burner 未提交。报告和回执保留状态码、版本和哈希，省略了本地运行位置和原始日志。

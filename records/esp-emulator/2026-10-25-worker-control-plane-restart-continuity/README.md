# ESP Emulator Worker Control-plane Restart Continuity

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device control-plane restart scope）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`658b2d494bbd40fcb798ed4349a6304d46c0d917`
- 功能提交：`f85b8c9ef15f760c0c25fc7a70f3dbec53cbf050`
- 文档/失败证据提交：`cd0308025309fcb6dfd373502e87890449a1f98c`
- 功能 CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40141191663>
- 最终 CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40141285611>
- 环境：macOS Apple Silicon；两个真实 Device Service；真实 StickS3 QEMU；WorkerAgent

## 结论

central control plane 和 worker-local runtime 分成两个真实 Device Service
后，worker claim job 后中央服务停止并复用同一 state dir 重启，实测
downtime `2.2s`。

WorkerAgent 现在对已 claim job 的 transient network/429/5xx 做有界
heartbeat/result retry：

- 恢复后幂等重注册相同 `worker_id`、`instance_id`、`generation`；
- 使用原 `lease_id` 完成 heartbeat/result；
- 保留 worker-local QEMU session、evidence 收集和 cleanup ownership；
- terminal result 为 `completed/PASS`；
- evidence ZIP、runtime session stop 和 QEMU reap 均成立。

job queue terminal result 现在还保留 originating `lease_id`，使 lease 关闭后
仍可追溯 evidence 来自哪次 claim。

## 初始 FAIL 与根因

第一轮控制面重连本身已成功，但真实 `runtime=qemu` session 立即失败：

```text
cannot access local variable 'nic' where it is not associated with a value
```

根因是 device_service 的 QEMU launch path 只在 qemu-wifi/unified 分支中给
`nic` 赋值，却在后续 S3 WiFi 环境设置中无条件读取。非网络 `runtime=qemu`
因此被 Python `UnboundLocalError` 终止。

修复为在条件分支前初始化 `nic=None`。失败证据和成功证据分别保留，未把
初始 FAIL 归因成控制面重连失败或固件缺陷。

后续在 same-host HTTP/worker contracts 上补齐 lease ownership fencing：
re-claim 后旧 heartbeat/result 返回 `409 job_lease_mismatch`；
WorkerAgent 在 ownership 丢失或恢复超时后停止可达的 worker-local runtime，
并拒绝上报 stale result。见
[Follow-up: lease ownership fencing](followups/2026-10-25-lease-ownership-fencing/)。

## 关键证据

- 平台测试：`393/393 PASS`；
- 文档契约：`20/20 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- 真实 job：central restart 前 `leased`，恢复后 `completed/PASS`；
- downtime：`2.2s`；
- 同 worker/instance/generation/lease：`PASS`；
- evidence ZIP：`6,696 bytes`；
- evidence SHA256：
  `12713499ab0ce03087426d5adfedf3902658b799fed35f214d9d8c2c51385235`；
- runtime session stopped、QEMU process absent：`PASS`；
- token 未进入 worker log；
- functional CI `40141191663` 与最终 CI `40141285611` 均通过。

源码证据：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/cd0308025309fcb6dfd373502e87890449a1f98c/tests/network/worker_control_restart/evidence-2026-10-25-central-restart-pass.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/cd0308025309fcb6dfd373502e87890449a1f98c/tests/network/worker_control_restart/evidence-2026-10-25-initial-runtime-qemu-failure.json>

## 文件

- `report.md`：设计、失败定位、执行和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏聚合证据。

## 未覆盖项

- runtime service 重启或跨主机 QEMU 进程迁移；
- claim 请求在响应丢失后的自动恢复；当前没有稳定 claim dedup token，
  因此 claim 本身不盲目重试；
- companion HTTP/BLE/evidence-stream continuity；
- 跨子网/NAT discovery、生产多机 scheduler；
- physical hardware validation。

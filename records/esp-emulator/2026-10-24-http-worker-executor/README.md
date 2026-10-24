# ESP Emulator HTTP-only worker executor

- 日期：`2026-10-24`
- 结果：`PASS`（同主机真实 QEMU job）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`b31c3ab6d827b7e2a7199e3e30e75952fe4eaa20`
- 结果版本：`d200bada9e72593db21cdfb191cdb59e488439a4`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40056513345>
- 环境：macOS Apple Silicon；真实 StickS3 QEMU；Device Service；Python 3

## 结论

新增独立 `platform/tools/worker_agent.py`，仅使用公开 `/api/v1`：

- 持久 worker ID、instance ID 和递增 generation；
- 注册远程 worker 并周期 heartbeat；
- claim durable job；
- 执行期间同时续 worker 和 job lease；
- 创建真实 Device Service session；
- 等待 `running`，下载 evidence ZIP 并计算 SHA256；
- 以 `purge=0` 停止 session；
- 提交 completed/PASS 或 FAIL；
- 干净退出时将 worker generation 标记 stopped。

真实 live job 已通过：agent 通过公开 API claim 一个 queued StickS3 job，
创建真实 QEMU session，下载 6891-byte evidence ZIP，停止 session，提交
attempt 1 / completed / PASS，agent exit 0。

## 关键证据

- 平台测试：`292/292 PASS`；
- worker agent：`3/3 PASS`；
- live executor：`1/1 PASS`；
- evidence SHA256：
  `fda2344faabda7e1b8c4335a22dc51e4eedb448274ddc2bb8e307e599c62ca26`；
- GitHub Actions：`Ran 292 tests`、`OK (skipped=2)`，两个 job 均成功；
- source executor evidence SHA256：
  `8b3f066209ffbeac02c82502be73b0f0fb7d137d5dfb34ff354e273a88329306`。

## 文件

- `report.md`：执行状态机、真实 job 和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合证据。

源码证据：
<https://github.com/m5agent/m5stack-esp-emulator/blob/d200bada9e72593db21cdfb191cdb59e488439a4/tests/network/worker_executor/evidence-2026-10-24-executor-pass.json>

## 未覆盖项

- 跨主机 worker 通信；
- worker authentication/authorization hardening、lease fencing；
- companion HTTP/BLE/evidence continuity after service restart；
- 跨主机 QEMU re-attach；
- 生产多机容量调度和 warm pool；
- 恶意固件隔离；
- 物理硬件验证。

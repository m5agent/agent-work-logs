# ESP Emulator Worker Network-Partition Side-Effect Fencing

- 日期：`2026-10-25`
- 结果：`PASS`（virtual control-plane validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`667c3564208fcb69df7afea68091d6d3e34d3eb4`
- 结果版本：`fa902c2c3f67b560d4d7d64b8b1df302b4fa1067`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40160702972>
- 环境：Linux privileged Docker；两个独立 network namespace；GitHub Actions Ubuntu

## 结论

Worker 到 central control plane 的 traffic blackhole 现在不会再被单个默认
60 秒 HTTP socket timeout 拖住。每次 registration/heartbeat 请求的 timeout
受剩余 control reconnect budget 限制。

真实 namespace fixture 中：

- attempt 1 claim job，worker-local authenticated runtime 创建 running session
  和 600 秒 child side effect；
- nftables 只阻断 worker→central control traffic，本地 runtime 仍可达；
- heartbeat 在约 2 秒内失败，worker 设置 `lease_fenced=true`；
- worker DELETE runtime session、reap child process，并拒绝提交 stale result；
- central 的 5 秒 job lease 到期后重新排队；
- 网络恢复后 attempt 2 由第二个 worker 完成 job，terminal result `PASS`。

三个独立运行均通过，每轮 `18/18` checks，工具哈希无漂移。

## 关键证据

- 独立运行：`3/3 PASS`；
- 每轮 checks：`18/18 PASS`；
- attempt 数：每轮 `2`；
- attempt 1：local FAIL / `lease_fenced=true` / runtime process reaped；
- attempt 2：terminal `PASS`；
- platform tests：`444/444 PASS`；
- documentation contracts：`30/30 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- GitHub Actions `platform-contracts` 与
  `network-namespace-policy`：`PASS`；
- CI `network-namespace-policy` 实际执行新增 partition-fencing step 并成功。

源码 evidence：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/fa902c2c3f67b560d4d7d64b8b1df302b4fa1067/tests/network/worker_partition_fencing/evidence-2026-10-25-partition-fencing-3x.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/fa902c2c3f67b560d4d7d64b8b1df302b4fa1067/tests/network/worker_partition_fencing/run_test.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/fa902c2c3f67b560d4d7d64b8b1df302b4fa1067/tests/network/worker_partition_fencing/runtime_fixture.py>

## 文件

- `report.md`：根因、实现、topology、执行和回滚；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `evidence/partition-fencing-3x.json`：三次独立运行汇总。

## 未覆盖项

- QEMU/device-specific side-effect fencing；
- worker 未拥有的外部网络或宿主 side effect；
- 物理跨主机 QEMU executor/reattach；
- production scheduler、object storage 和 untrusted-firmware VM；
- physical hardware/RF/power validation。

# ESP Emulator Worker Network-Partition Side-Effect Fencing

- 日期：`2026-10-25`
- 结果：`PASS`（virtual control-plane validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`667c3564208fcb69df7afea68091d6d3e34d3eb4`
- 功能与证据提交：`ff605757d20e0954cfcbbde4bc3bbd1381e8065d`
- 最终结果版本：`9e88699199b8b473d1fb74b581931a398f4b68ca`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40163740320>
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

同一 runner 的真实 worker-local QEMU lane 也连续 `3/3 PASS`：worker
namespace 内独立 Device Service 上传完整 StickS3 image、创建真实 QEMU
session；断网后 attempt 1 被 fence，QEMU PID 被回收，attempt 2 启动新
QEMU 并完成 job。

最终 runner 又把 lane 扩展到 `qemu-unified`。三个独立运行都在 partition
前要求同一 session 出现 HTTP request、BLE PASS 和非空 pcap；断网后
attempt 1 被 fence，HTTP/BLE companion 进入 `terminated`、BLE PID 消失、
pcap summary 完成；attempt 2 启动新 unified session，再次完成 HTTP/BLE/pcap
和 terminal PASS。每轮 `30/30` checks。QEMU 内 guest/device-controller
内部状态、worker 未拥有的外部 side effect、物理跨主机和真机仍为 `NOT RUN`。

## 关键证据

- 独立运行：`3/3 PASS`；
- 每轮 checks：`18/18 PASS`；
- attempt 数：每轮 `2`；
- attempt 1：local FAIL / `lease_fenced=true` / runtime process reaped；
- attempt 2：terminal `PASS`；
- QEMU lane：`3/3 PASS`，每轮 attempt 1 QEMU PID reap、attempt 2 新
  QEMU terminal `PASS`；
- Unified lane：`3/3 PASS`，每轮 `30/30` checks；partition 前 HTTP request
  1、BLE PASS、pcap 非空；fence 后 companion terminated、BLE PID 回收、
  pcap summary `PASS`，retry 重新取得 unified evidence；
- platform tests：`447/447 PASS`；
- documentation contracts：`33/33 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- GitHub Actions `platform-contracts` 与
  `network-namespace-policy`：`PASS`；
- CI `network-namespace-policy` 实际执行新增 partition-fencing step 并成功。

源码 evidence：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/2dd44b2b78fb3463ff2be9cb36321b19e93f49d3/tests/network/worker_partition_fencing/evidence-2026-10-25-partition-fencing-3x.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/2dd44b2b78fb3463ff2be9cb36321b19e93f49d3/tests/network/worker_partition_fencing/evidence-2026-10-25-partition-fencing-qemu-3x.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/2dd44b2b78fb3463ff2be9cb36321b19e93f49d3/tests/network/worker_partition_fencing/run_test.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/2dd44b2b78fb3463ff2be9cb36321b19e93f49d3/tests/network/worker_partition_fencing/runtime_fixture.py>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/ff605757d20e0954cfcbbde4bc3bbd1381e8065d/tests/network/worker_partition_fencing/evidence-2026-10-25-partition-fencing-unified-3x.json>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/ff605757d20e0954cfcbbde4bc3bbd1381e8065d/tests/network/worker_partition_fencing/run_test.py>

## 文件

- `report.md`：根因、实现、topology、执行和回滚；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `evidence/partition-fencing-3x.json`：三次独立 process-lane 运行汇总；
- `evidence/partition-fencing-qemu-3x.json`：三次独立真实 QEMU lane 汇总。
- `evidence/partition-fencing-reconciled-3x.json`：最终 runner 的 process
  lane 复跑；
- `evidence/partition-fencing-qemu-reconciled-3x.json`：最终 runner 的
  plain-QEMU lane 复跑；
- `evidence/partition-fencing-unified-3x.json`：最终 runner 的
  `qemu-unified` companion/pcap lane。

## 未覆盖项

- QEMU 内 guest/device-controller side-effect fencing；
- QEMU 内 guest/controller 内部状态；
- worker 未拥有的外部网络或宿主 side effect；
- 物理跨主机 QEMU executor/reattach；
- production scheduler、object storage 和 untrusted-firmware VM；
- physical hardware/RF/power validation。

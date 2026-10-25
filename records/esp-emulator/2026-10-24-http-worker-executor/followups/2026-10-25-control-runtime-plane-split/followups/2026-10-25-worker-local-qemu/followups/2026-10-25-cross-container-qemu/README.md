# ESP Emulator worker QEMU across Docker containers

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）；physical cross-host/hardware
  `NOT RUN`
- 工作类型：`code_change`
- 源码版本：
  `https://github.com/m5agent/m5stack-esp-emulator/commit/c4408b4937881a97b802b383ad9c5a9bf70b3685`
- Base commit：`c2083ecddb553eaddbf69fabeb6abbb1218b22dc`
- 环境：macOS arm64 host；Docker linux/arm64 29.8；Ubuntu 25.04 pinned
  digest image；Python 3.13；真实 Linux arm64 QEMU

## 结论

central control plane 与 worker-local runtime/QEMU 已从同一主机的两个
network namespace 推进到两个独立 Docker 容器：

- central 容器拥有 durable queue、worker directory 和 control API；
- worker 容器运行 `worker_agent` 与独立 runtime Device Service；
- 两者只通过 user-defined Docker bridge 通信；
- worker runtime 创建真实 StickS3 QEMU session；
- source firmware、normalized firmware 和 QEMU SHA256 均绑定；
- manifest/serial/QOM evidence 回到 central terminal job；
- terminal 为 `completed/PASS`，`execution_plane=worker-local`；
- token 未进入日志，QEMU、两个容器和 bridge 均清理。

三个独立运行均 PASS，所有稳定源码/产物哈希一致。

## 关键证据

- fixture checks：`21/21 PASS`；
- 运行耗时：`11.708s`、`11.680s`、`11.589s`；
- firmware source/normalized SHA256：
  `53170651ccabc8fb16b5cf993d348693c12bcc643a6f0c60bf7a479d8a456c73`；
- QEMU SHA256：
  `f024f034d20bd5b8e2c224ce69deed70984b0514f8a310d221b388b74c179ecb`；
- platform tests：`428/428 PASS`；
- docs contracts：`25/25 PASS`；
- CI `40154787407` 两个 job PASS；
- 两次早期失败分别定位为容器代理环境未清除，以及宿主绝对 QEMU 路径被
  传入容器；修复后的三次运行均 PASS。

## 文件

- `report.md`：拓扑、故障、修复、执行和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏 3× run 与 CI 摘要。

## 未覆盖项

- 物理独立主机；
- 跨主机进程迁移或 re-attach；
- NAT/跨子网 discovery；
- companion HTTP/BLE continuity；
- 生产多主机调度；
- physical RF/hardware validation。

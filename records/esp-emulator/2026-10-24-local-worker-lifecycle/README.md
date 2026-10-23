# ESP Emulator Local Worker Lifecycle

- 日期：`2026-10-24`
- 结果：`PASS`（virtual-device worker control）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`689c49b77ff6595a97dc57d3b3e6b37bef7fde8d`
- 基线版本：`8e37781326e337d1d479b3dd432099f4734e8c16`
- 环境：macOS Apple Silicon；本地 Device Service；StickS3 QEMU；Ubuntu GitHub Actions

## 结论

本地 Device Service 现在有持久化 worker 控制面：

- 稳定 worker ID、每进程 instance ID 和 generation；
- 独占状态目录锁，第二个 live worker fail-closed；
- heartbeat、stale 判定、active lease 和 bounded recent results；
- `GET /worker`、`POST /worker/drain`、`POST /worker/resume`；
- drain 时拒绝新 lease，但活动 QEMU 会话继续运行；
- 最后一个 lease 停止后自动进入 `drained`；
- 强制终止服务进程组后，下一代 worker 将旧 lease 记录为 abandoned，
  对应会话恢复为 interrupted `failed` history；
- 真实 `qemu-wifi` lease 的 worker result 保留 pcap availability。

这是本地 lifecycle 里程碑。远程 worker 注册/调度、活动 QEMU 进程 re-attach、
warm pool、多机和恶意固件 VM 隔离仍为 `NOT RUN`。

## 关键证据

- Worker lifecycle fixture：17/17 checks PASS；
- 真实 StickS3 `qemu-wifi` session：frame 可读、pcap 可用，
  network evidence 为 `PARTIAL`，没有冒充网络 PASS；
- 强杀后 worker generation `1 → 2`，active lease 归零，abandoned lease 计数为 1；
- 平台测试：`264/264 PASS`；
- GitHub Actions：run `40037664731` 全绿；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：设计、执行、证据和边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：公开脱敏证据摘要

## 未覆盖项

- 远程 worker 注册、队列、heartbeat ingestion 和 scheduler；
- 活动 QEMU 进程跨服务重启 re-attach；
- warm pool、多主机、迁移和 drain deadline；
- 外部 IPv6、VM/租户隔离和恶意固件安全边界；
- 物理硬件与 RF。

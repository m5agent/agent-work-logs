# ESP Emulator P0 网络 CI、虚拟 radio 恢复与 eFuse 安全证据

- 日期：`2026-10-24`
- 结果：`PASS`（声明的虚拟设备/静态证据范围）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`34032874250d93e01657dbe389a6a832648d172f`
- 结果版本：`829d64e99ae318c6d78de0729bb6a75f8455373c`
- 环境：macOS Apple Silicon；GitHub Actions Ubuntu；现有 QEMU runtime

## 结论

本轮关闭三项可执行 P0 子任务：

1. GitHub Actions 现在运行完整平台测试和 Linux namespace/nftables egress
   fixture，并保存 evidence artifact。
2. StickS3 在同一个 QEMU guest 内完成 scan `1→0→1`：关闭 WiFi 模型
   `radio-enabled` 后看不到 AP，恢复后重新 DHCP 并通过 `/after` HTTP；pcap
   同时记录两组 DORA。
3. FirmwareManifest 可解析真实的 `espefuse summary --format json` stdout，
   分离镜像、sdkconfig、分区 flag 与 eFuse 证据；原始 key/value 不复制到
   输出，启用 secure boot/Flash Encryption 时 capability preflight 仍拒绝。

Core2 stock native-VHCI 仍依赖 QEMU GDB bridge，未在本轮声称生产化完成。

## 关键证据

- GitHub Actions：完整 `239/239` 平台测试、catalog/coverage/profile checks、
  Ubuntu namespace + nftables exact IPv4 egress 全部 PASS；
- radio loss：`RECONNECT RADIO_DOWN_SCAN 0`、
  `RECONNECT RADIO_RESTORED_SCAN 1`、两次 DHCP、HTTP 200 before/after；
- eFuse：真实 espefuse v5.6.0 虚拟 summary 的 89 个字段可解析；合成启用状态
  推导出 secure boot v2 + Flash Encryption，敏感 sentinel 未进入 manifest/输出；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：实现、验证和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合证据。

## 未覆盖项

- Core2 无 GDB native controller；
- Core2 物理 cache/PSRAM、RF、coexistence 和 soak；
- 双设备 fabric、外部 IPv6、自托管 QEMU worker；
- 真机 eFuse 读取、生产 key 和物理硬件安全链。

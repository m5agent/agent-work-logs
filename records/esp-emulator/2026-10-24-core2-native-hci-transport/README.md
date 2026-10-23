# ESP Emulator Core2 native HCI transport

- 日期：`2026-10-24`
- 结果：`PASS`（QEMU host transport-only）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`b62cd3715bd1d3eca3b7550a12249585f5c8c6f6`
- 结果版本：`f32ae621454a1fb52aaa3b8313db923622161a92`
- 环境：macOS Apple Silicon；QEMU 9.2.2 Xtensa；`m5core2`

## 结论

新增 QEMU `esp32-native-hci` chardev frontend，完成 `CORE2-01` 的第一个
非 GDB 切片（HCI-1 transport-only）。

已验证 H4 event 与分片 ACL 的 framing、32-packet bounded RX queue、
overflow drop、peer open/close counters 和 clean shutdown。QEMU patch
通过 forward/reverse apply。

该结果不表示 stock guest VHCI、C2H callback 或 native BT controller 已接通；
H2C guest capture、vCPU-safe C2H commit、BLE discovery/GATT 和 repeated
Device Service lease 仍为 `NOT RUN`。

## 关键证据

- QEMU transport targeted test：11 项检查 PASS；
- RX queue：2 packets/15 bytes，随后填满 32 并丢弃第 33 个；
- peer opened/closed 和 QEMU exit code 0；
- QEMU patch SHA256：
  `6a7d06ba5580cc9b3146258cfeb1ac13274b71782d8513373a4ef546ce678f95`；
- 平台测试：`243/243 PASS`。
- GitHub Actions `40010243257`：`platform-contracts` 与
  `network-namespace-policy` PASS。

## 文件

- `report.md`：实现、复用边界和验证；
- `run.json`：结构化记录；
- `evidence/summary.json`：脱敏聚合结果。
- `followups/2026-10-24-guest-h2c-capture/`：后续无 GDB 捕获 stock
  HCI Reset，完整 sequence 仍等待 C2H。

## 未覆盖项

- guest H2C 从 `vhci_env_p`/`API_vhci_host_send_packet` 进入 QEMU transport；
- Bumble C2H 在 vCPU 安全点进入 firmware `notify_host_recv`；
- stock BLE scan/connect/NUS；
- repeated Device Service lease；
- bit-exact controller/baseband、RF、coexistence 和物理硬件。

# ESP Emulator Core2 HCI-3b API-Boundary Audit

- 日期：`2026-10-24`
- 结果：`PARTIAL`（审计完成；完整 GATT 仍失败）
- 工作类型：`service_debug`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`e5fbf39af5e69fb383249ab0a3b2fa88ac916c26`
- 基线版本：`aeb21e2027c3b821098e680fa5cb163d04ed7eec`
- 环境：macOS Apple Silicon；QEMU m5core2；stock UIFlow2 Core2；Bumble controller/peer

## 结论

`HCI-3b` 仍未通过，但失败边界已经进一步收敛：

- 原 native-HCI 只观察内部 controller 的 H2C 写入，导致固件 controller 与
  Bumble 同时推进 HCI 状态；
- GDB 5/5 路径实际在 `API_vhci_host_send_packet` 入口 bypass 内部 controller；
- Xtensa API 断点发生在 `entry` 前，返回时不得旋转 `WINDOW_BASE`；
- 按正确返回语义实现的实验性 QEMU API hook 已通过广播、连接、NUS service
  discovery 和 CCCD subscription，并让 Bumble 发出 NUS write；
- 最后 guest write/notification 事务仍不稳定，`HCI-3b` 保持 `FAIL`。

实验性 QEMU/API hook 代码未保留。当前结论是可以继续实现的安全依据，不是已完成
native Bluetooth backend。

## 关键证据

- GDB pre-entry 返回：API PC `0x403064d8` → wrapper call site
  `0x402670a8`，`WINDOW_BASE` 保持不变；
- internal-controller relay：第二个 ATT request 后 ACK 12/Reset；
- best API-hook run：GATT discovered/subscribed true，write 已到 guest，
  final write/notify false；H2C parser error/drop 为 0；
- 增加 nested callback budget 只改变失败点，没有闭环；
- 平台测试：`264/264 PASS`；
- GitHub Actions：run `40041254086` 成功；
- 物理硬件、RF 与 coexistence：`NOT RUN`。

## 文件

- `report.md`：实验、寄存器语义、结果与边界；
- `run.json`：机器可读记录；
- `evidence/api-boundary.summary.json`：公开脱敏实验摘要；
- `evidence/github-actions.summary.json`：对应源码 commit 的 CI 回读。

## 未覆盖项

- 完整 scan/connect/service discovery/subscribe/write/notify `PASS`；
- `HCI-4` 无 GDB Device Service repeated lease；
- bit-exact Espressif BT controller/baseband；
- 物理硬件、RF、coexistence 和 soak。

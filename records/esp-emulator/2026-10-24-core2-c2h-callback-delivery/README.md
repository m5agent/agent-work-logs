# Core2 QEMU 原生 HCI C2H callback 交付

- 日期：`2026-10-24`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`5217b50af60c7ac31f3051a6fef8b70fdb110fe4`
- 基线版本：`53cefc14e909519baebf12784597c3274f72f1e4`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40019731626>
- 环境：macOS Apple Silicon；QEMU 9.2.2 M5Stack worktree；stock Core2 UIFlow2

## 结论

`HCI-3a` 单包 C2H callback 已通过并连续 `5/5`：

- dummy controller 从 guest 收到 HCI Reset `01030c00`；
- QEMU 返回 Reset Complete `040e0401030c00`；
- QEMU 从 `vhci_env_p + 0x4e4` 读取 firmware 注册的
  `notify_host_recv`，用 guest `malloc` buffer 交付；
- callback 状态为 `0`，随后调用 send-available；
- guest 继续发出 Read Local Version `01011000`；
- QOM、dummy peer 和 clean shutdown 检查全部 PASS。

这证明 callback ABI、guest buffer、Xtensa call8 window/return、safe point
和 H2C/C2H 往返的基本路径。它不证明完整 BLE：探索性 Bumble 运行可完成
HCI 初始化、广播和连接，但 ATT/GATT sequence 尚不稳定，因此完整
`HCI-3b`、`HCI-4` repeated lease 和 bit-exact controller 仍未完成。

## 关键证据

- targeted C2H callback：`5/5 PASS`；
- 单次 committed evidence：Reset → Reset Complete → next H2C；
- 平台测试：本机与 GitHub Actions 均为 `243` tests，CI `OK (skipped=2)`；
- QEMU patch reverse apply、forward apply 和重建 PASS；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- 固件 SHA256：`906ba16439f8f8b421adb9ba3817ebf91d677498b0096c38e851a63570a8b680`；
- QEMU SHA256：`f5ec86620e29fa2854ecb0bff6c480a794757cb1e9fe62069352183434dfb15e`。

## 文件

- `report.md`：实现、ABI、验证和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：聚合验证结果。

## 未覆盖项

- 完整 Bumble HCI init、ATT/GATT discovery、NUS subscribe/write/notify；
- Device Service repeated lease `5/5`；
- bit-exact ESP32 BT controller/baseband；
- RF、coexistence、physical cache/PSRAM 和真机验证。

# ESP Emulator Core2 stock native-VHCI BLE GATT

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：Core2 原生 Bluetooth controller 数据面缺口
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`1546798de9db5df52e3045527281c2a8d01dcc4d`
- 基线版本：`11bdf8fc3ed0588b4fb2ad7783d6b894489588fb`
- 环境：macOS Apple Silicon；QEMU `m5core2`；Bumble controller/peer

## 结论

stock Core2 UIFlow2 的内置-controller 构建现在可以不改 HCI transport，直接在
QEMU 中拦截固件真实的 `esp_vhci_host_*` H2C/C2H 边界，并把 controller 数据面
交给 Bumble。

外部 peer 完成 scan、connect、NUS service discovery、TX subscription、RX
write，guest 收到 `M5_CORE2_PROBE` 并返回 notify `ACK:M5_CORE2_PROBE`。独立
runner 连续 `5/5 PASS`。

该 PASS 的范围是 stock firmware 的 controller API 边界，不是 Espressif BT
baseband/controller 的 bit-exact 执行。

## 关键证据

- stock internal-controller firmware SHA256：
  `906ba16439f8f8b421adb9ba3817ebf91d677498b0096c38e851a63570a8b680`；
- native-VHCI runner：`5/5 PASS`；
- 每次均命中 serial RX/ACK、peer found/connect/GATT/subscribe/write/notify、
  bridge H2C/C2H 和 ACL H2C/C2H marker；
- 平台测试：`213/213 PASS`；
- Core2 peripheral matrix：`6/6 PASS`；
- Core2 device frame/input matrix：`1/1 PASS`；
- physical hardware：`NOT RUN`；
- bit-exact Espressif BT controller/baseband：`NOT RUN`。

## 文件

- `report.md`：实现、执行、证据和边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：脱敏聚合证据

## 未覆盖项

- 把 GDB 诊断桥生产化为 QEMU 内部组件或 Device Service worker；
- 在同一 unified lease 中同时保留 frame/QOM/WiFi 和 native-VHCI BLE；
- 执行 bit-exact Espressif BT baseband/controller；
- RF、coexistence、配对/安全、吞吐、soak 和真机验证。

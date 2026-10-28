# ESP Emulator：ESP-NOW loopback 与三设备接口最终复测

- 日期：`2026-10-28`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：StopWatch / StickS3 / Core2 的 UIFlow2 全接口复测与 ESP-NOW
  controller data-plane 缺口
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`805925d8`](https://github.com/m5agent/m5stack-esp-emulator/commit/805925d8336fac28652d5bddfa1df0ec4b1606b8)
- 结果提交：[`9f9c31c7`](https://github.com/m5agent/m5stack-esp-emulator/commit/9f9c31c7b42d569391fef3f338d20d5b6a81a34c)
- 环境：macOS arm64、QEMU TCG single-thread/icount、独立 Device Service
  session；不记录内部端点或设备唯一标识

## 结论

新增默认关闭的 `0067` ESP-NOW controlled-peer loopback。三台原厂 UIFlow2
`v2.5.3` 通过正常 controller TX/RX DMA 完成 unicast、broadcast、receive
和 IRQ；同 guest 的 `espnow.ESPNow`、`ESPNowBase`、`m5espnow.M5ESPNow`
也通过 `send`、`recvinto`、`irq`。这关闭了 controller loopback 子缺口，
但不证明外部 peer、PMK 加密 payload、跨设备 fabric、丢包/重试或 RF。

最终 QEMU `c3c31403…` 同时完成三台 system/shared、17 个设备组、
sockets/MQTT/network/EzData、audio wrapper、requests/Modbus candidate
和 TLS candidate 回绑。全部为 virtual-device validation；physical
hardware 为 `NOT RUN`。

## 关键证据

- QEMU SHA256：`c3c3140322513de6f3ef724513e2f1272764e6af8a8fdd7c7bfd4448dc17f534`
- `0067` SHA256：`d269334ac039e78a75cc3054c4f6e853865cb16f7489a242c40ddf095a57163b`
- 三设备 system：各 `50 PASS + 1 STATE_PASS`
- 三设备 shared corrections：各 `7/7`
- 设备组：StopWatch `6/6`、StickS3 `5/5`、Core2 `6/6`，无 retry
- audio：StopWatch/StickS3 player `15/15`、recorder `12/12`
- TLS candidate：三台各 `5/5`
- platform tests：`1362` 项，`OK (skipped=1)`
- GitHub CI
  [`40683135452`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40683135452)
  的 `platform-contracts` 与 `network-namespace-policy` 两个 job PASS；
- 主仓证据：[`ESP-NOW loopback 与三设备接口复测`](https://github.com/m5agent/m5stack-esp-emulator/blob/9f9c31c7b42d569391fef3f338d20d5b6a81a34c/docs/evidence/2026-10-28-espnow-and-three-board-interface-retest/README.md)

## 文件

- `report.md`：根因、改动、执行、证据和边界
- `run.json`：机器可读结果
- `evidence/`：脱敏结果摘要
- `patches/README.md`：patch hash、ordering 和 reverse-check
- `code/`：不适用；可重建测试位于主仓

## 未覆盖项

- ESP-NOW 外部/加密 peer、cross-device fabric、loss/retry、RF/timing：
  `RUNTIME-06`；
- Core2 legacy UIFlow normal-WDT reset、display completion、setup/REPL
  和非空帧：`RUNTIME-03`；
- Core2 全部 28 类 M5UI 文档方法矩阵：`REVIEW`；
- 物理硬件、RF、声学、光学和电气：`NOT RUN`。

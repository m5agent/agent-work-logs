# ESP Emulator 三设备并发复测与 runner 竞态修复

- 日期：`2026-10-28`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户要求在 StopWatch、StickS3、Core2 上并发复测 UIFlow2 接口，并统一解决发现的问题
- 源码版本：`https://github.com/m5agent/m5stack-esp-emulator` @
  `5abfeac88029f549ff496a6397b6dc2baffa3e69` → `90f556387560a47230141946e96f6f0166266721`
- 环境：macOS arm64；Device Service `/api/v1`；TCG virtual device；物理硬件未使用

## 结论

三台设备以设备间并发、设备内串行完成 UIFlow2 system、shared corrections、
网络协议、输入和音频复测。发现并修复两个测试基础设施竞态：

1. 多个 `qemu-wifi`/`qemu-unified` 会话竞争固定 controlled HTTP fixture 端口；
2. 串口 READY 可能早于 session 发布 `running`，导致首个输入 action 被 409 拒绝。

同时把 bounded marker action 的上限从 10 秒放宽到 30 秒，以匹配 Core2 的
18 秒首等待。修复后并发 sockets/network、两路 unified ESP-NOW loopback、
BtnA/WAS_HOLD 和 Core2 顺序设备 case 均通过。

原厂固件的 HTTP、Modbus async 和 M5UI 源码缺陷仍保留，不能用本轮模拟器测试
基础设施修复关闭。

## 关键证据

- QEMU SHA256：
  `6ff2aca091909ea078e5b9805b420cb04c11e3f9928b52c2fac199e33e45b2ef`
- StopWatch firmware：
  `99d6482befe094de47bf68ce43618d3868bd62fb1fc72f0b55c0d0c2ea4e7f8d`
- StickS3 firmware：
  `c08196024019273ccadee9b4b3da303567f7ab206fa14edd1af283f04f6e98d8`
- Core2 firmware：
  `b228c0e2d877e77a8a352e917ed84f4da8ea92d15b25e28f431a2999620fe3c4`
- 三台 system runtime：各 `50 PASS + 1 STATE_PASS`
- 三台 shared corrections：各 `7/7`
- sockets/MQTT/network/EzData：`23/23`、`42/42`、`14/14`、`17/17`
- StopWatch/StickS3 audio：player `15/15`；recorder `12/12`
- Core2 顺序 cases：peripherals `6612`、IMU `3766`、AXP192 `3917`
  nonblack pixels，全部 PASS
- Device Service API sweep：`81` operations、`95` cases、全部 PASS
- Platform tests：`1364` 项 `OK`，`1` skipped
- Generated checks：runtime coverage、peripheral catalog、QEMU profiles、
  project snapshot 全部 PASS
- GitHub CI：`platform-contracts` 与 `network-namespace-policy` 两 job PASS

## 文件

- `report.md`：根因、修复、执行和边界
- `run.json`：结构化结果
- `evidence/summary.json`：脱敏结果摘要

## 未覆盖项

- Core2 legacy UIFlow 的正常 WDT、启动 UI、setup/REPL 和完整应用帧；
- 外部/加密 ESP-NOW peer、RF、timing 和跨设备 fabric；
- Core2 完整二十八类 M5UI 文档矩阵；
- 物理硬件、触控压力、显示时序、声学、光学和电气验证。

## 后续

- [StopWatch / StickS3 / Core2 UIFlow2 全接口复测](followups/2026-10-29-three-board-uiflow2-full-retest/)：
  完成 505 方法 M5UI 矩阵、完整通信/ESP-NOW/音频/已选外设复测，并修复
  M5UI 尺寸/旋转、Core2 预算、BLE identity 和 blocker 文案。
- [三设备 UIFlow2 接口矩阵与 RMT API 夹具](followups/2026-10-28-rmt-api-and-interface-matrix/)：
  完成其余协议组、StickS3 IR TX/RX、三台 UI/输入验证，并补齐
  trusted-local RMT 文件接口白名单。

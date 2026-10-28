# ESP Emulator StopWatch / StickS3 / Core2 UIFlow2 全接口复测

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：用户要求在 StopWatch、StickS3、Core2 上并发复测所有可执行
  UIFlow2 接口，汇总后统一处理测试侧问题
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`bc0f4609`](https://github.com/m5agent/m5stack-esp-emulator/commit/bc0f4609795fd995ffae6211c5997d21be9f5f80)
- 环境：macOS arm64、隔离 Device Service `/api/v1`、三设备 QEMU TCG；
  物理硬件未使用

## 结论

三台当前原厂 UIFlow2 `v2.5.3` 已完成 system、shared corrections、
sockets/MQTT/network/EzData/EasySocket、音频、ESP-NOW、BLE 最小路径、
已选板级外设和 StopWatch/Core2 全量 M5UI 方法矩阵复测。

本轮统一修复了四个测试端问题：

1. M5UI runner 使用设备清单的 `api_size` 和 `ui_rotation`，不再把 Core2
   固定为 `320x240/rotation=0`；
2. 慢速 Core2 program 使用可配置、最高 120 秒的请求和 marker 预算；
3. BLE 广告身份和 ACK payload 覆盖完整五设备映射，与 Device Service
   保持一致；
4. Core2 radio blocker 不再错误描述为 ESP32-S3。

测试侧修复后，三台 stock BLE 仍被内部 controller/board-ready 边界阻塞。
Stock M5UI 仍复现 Canvas triangle、Image float scale 和 integer Spinbox
step 三个缺陷；StopWatch candidate 状态与画面通过，Core2 candidate 状态
`4/4` 通过但全屏刷新帧仍有条带/坐标错误。Core2 legacy `RUNTIME-03`
保持 `OPEN`。

## 关键证据

- QEMU SHA256：
  `fccfa931c032f8cae6b90e97ba5f98b1770fbf6856446c4db5f7950241e1fe90`
- StopWatch/StickS3/Core2 原厂基础镜像：
  `99d6482b…`、`c0819602…`、`b228c0e2…`
- 三台 system：各 `50 PASS + 1 STATE_PASS`；shared：各 `7/7`
- sockets `23/23`、MQTT `42/42`、network `14/14`、EzData `17/17`
- EasySocket `57 PASS + 1 N/A`
- StopWatch/StickS3 audio player `15/15`、recorder `12/12`
- ESP-NOW 三台
  `12 PASS + 5 STATE_PASS + 1 CONFIGURED_UNVERIFIED`；
  native ESP-NOW
  `21 PASS + 21 STATE_PASS + 3 CONFIGURED_UNVERIFIED`
- StopWatch/Core2 M5UI：各 `28` 类、`505` 方法，分类完全一致：
  `407 STATE_PASS + 80 PENDING_FRAME_OR_INPUT +
  3 PENDING_FRAME_OBJECT_REMOVAL + 11 DOCUMENTATION_MISMATCH +
  1 EXPECTED_UNSUPPORTED + 3 FAIL`；`28/28` final frame 非黑
- Platform tests：`1406` 项 `OK`，`1` skip
- GitHub CI
  [`40750443386`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40750443386)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：
  [三设备全接口复测](https://github.com/m5agent/m5stack-esp-emulator/blob/bc0f4609795fd995ffae6211c5997d21be9f5f80/docs/evidence/2026-10-29-three-board-uiflow2-full-retest/README.md)

## 文件

- [report.md](report.md)：根因、改动、执行和验证边界
- [run.json](run.json)：机器可读结果
- [evidence/summary.json](evidence/summary.json)：脱敏计数、哈希和失败分类

## 未覆盖项

- Core2 M5UI full-screen refresh/window routing 与 candidate frame oracle；
- Core2 legacy UIFlow normal-WDT 启动 UI、setup/REPL 和完整应用帧；
- stock BLE internal-controller GATT、显式 HCI 跨固件兼容和真实 RF；
- 外部/加密 ESP-NOW peer、cross-device fabric、RF/timing；
- 物理硬件、触控、声学、光学和电气验证。

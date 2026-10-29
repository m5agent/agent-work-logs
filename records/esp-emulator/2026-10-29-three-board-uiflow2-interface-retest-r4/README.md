# ESP Emulator 当前 QEMU 三设备 UIFlow2 接口复测 r4

- 日期：`2026-10-29`
- 结果：`PARTIAL`（virtual-device；接口复测完成，stock SDK/BLE/legacy/真机边界保留）
- 工作类型：`report`
- 问题来源：用户要求并发复测 StopWatch、StickS3、Core2 的可测 UIFlow2 接口并统一处理发现的问题
- 源码版本：[m5stack-esp-emulator@32213028](https://github.com/m5agent/m5stack-esp-emulator/commit/322130288ea4fb2c2aab49b689e232bb2beef7f7)
- 环境：macOS arm64；三个隔离 Device Service；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

在 QEMU
`dd4b1b34a4003a6fe84263974efade9d8d85e584fcd7397bc0f13b2d77337435`
上重新并发复测三台设备。没有发现由当前 QEMU 引入的稳定接口回归；
system/shared、board display、通信、ESP-NOW、audio、BLE 和板级接口结果
保持。StopWatch/Core2 的 M5UI 507 项仍无漏测。

Core2 network 在三设备首轮并发即得到 `14/14 PASS`，相对 r3 首轮
`13/14` 改善。stock 固件的 requests2、Modbus async、TLS epoch、Core2
`m5ble.Server.get_client` 和 M5UI 三缺陷继续稳定复现；相同 stock base 上的
hash-pinned candidate 路径全部通过。

## 关键证据

- runtime：所有报告均为 `dd4b1b34…`；
- system：三台各 `50 PASS + 1 STATE_PASS`；
- shared：三台各 `7/7`；
- M5UI：StopWatch/Core2 各 29 sessions、507 results、0 unobserved；
- M5UI candidate：两台各 `4/4 STATE_PASS + 2/2 FRAME_PASS`；
- requests2/Modbus/TLS candidate：三台分别 `2/2`、`50/50`、`5/5`；
- Core2 BLE：stock NUS `8/8`，M5BLE stock `21 PASS + 1 ERROR`，
  candidate `22/22 PASS`；
- hardware matrix：三台各
  `115 CALL_OK + 66 API_ASSERTION_PASS + 1 OBSERVED`；
- platform：`1432` tests，`OK`，1 个既有 skip；
- CI：[40799810517](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40799810517)，
  `network-namespace-policy` 与 `platform-contracts` 均 PASS；
- 三个主服务和五个短生命 candidate 服务、QEMU、BLE peer 全部清理。

## 文件

- `report.md`：执行、控制实验、验证层和边界
- `run.json`：机器可读摘要
- `evidence/summary.json`：计数、哈希、失败和未运行项
- `patches/`：不适用，本轮没有新的模拟器源码修复
- `code/`：不适用，runner 和复现入口已在源码仓库

## 未覆盖项

- StopWatch/StickS3 stock internal-controller GATT；
- BLE pairing/security、RF、天线、共存和 controller bit-exact；
- 外部或加密 ESP-NOW、跨设备 fabric 和丢包/重试；
- Core2 legacy UIFlow `RUNTIME-03` normal-WDT 启动和应用帧；
- 物理硬件、声学、光学、电气和物理 PSRAM/cache timing；
- 本次是 `virtual-device validation`，不是 physical hardware validation。

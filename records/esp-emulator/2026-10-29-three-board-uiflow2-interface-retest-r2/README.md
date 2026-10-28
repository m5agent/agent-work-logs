# ESP Emulator StopWatch / StickS3 / Core2 UIFlow2 接口再次复测

- 日期：`2026-10-29`
- 结果：`PARTIAL`（virtual-device；可执行接口复测完成，stock SDK/BLE/legacy/真机边界保留）
- 工作类型：`code_change`
- 问题来源：用户要求并发复测三台设备全部可测 UIFlow2 接口并统一处理问题
- 源码版本：[m5stack-esp-emulator@490539ce](https://github.com/m5agent/m5stack-esp-emulator/commit/490539ce4aea7628154af56a2acd7c304ecc0e95)
- 环境：macOS arm64；三个隔离 Device Service；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

三台设备在 QEMU
`9bf74439ddbe7225a64eb437290043729fb032525756adb834565ec412f8c197`
上重新完成 system/shared、board display、通信、audio、ESP-NOW、板级接口和
可执行的 M5UI 方法矩阵。没有发现新的稳定功能回归。

stock 固件仍稳定保留 requests2、Modbus async、TLS epoch、Core2
`m5ble.Server.get_client` 和 M5UI 三项缺陷；相同 stock base 上的
hash-pinned candidate 路径全部通过。Core2 `m5ble` 最终 candidate 叠加
UUID32 与 sorted-client accessor 修正后为 `22/22 PASS`。

BLE teardown 的并发时序竞争和 client-role 准入误分类已在测试工具中修正，
分别采用 2 秒断连 settle 和 `NOT_RUN / BLOCKED_FIXTURE`。新增可复用的
`run_m5ui_matrix.py`，并增加 M5UI candidate preimage 准入与矩阵契约测试。

## 关键证据

- 平台：`1428` tests，`OK`，`1` existing skip；
- CI：[40777175035](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40777175035)；
- system：三台各 `50 PASS + 1 STATE_PASS`；
- shared：三台各 `7/7`；
- M5UI：StopWatch/Core2 各 `507` 个可观察结果、29 个 READY frame、零漏测；
- M5UI candidate：两台各 `4/4 STATE_PASS + 2/2 FRAME_PASS`；
- requests2/Modbus/TLS candidate：三台分别 `2/2`、`50/50`、`5/5`；
- Core2 BLE NUS：settle 后两轮各 `8/8`；
- 通用 hardware matrix：三台各 `115 CALL_OK + 66 API_ASSERTION_PASS + 1 OBSERVED`。

## 文件

- `report.md`：根因、改动、执行、验证和边界
- `run.json`：机器可读摘要
- `evidence/summary.json`：公开计数、哈希、失败与未运行项
- `patches/0001-m5ble-server-client-index.patch`：`0025` 候选修正
- `code/`：不适用；runner 与 tests 已随源码提交

## 未覆盖项

- StopWatch/StickS3 stock internal-controller GATT；
- BLE pairing/security、RF、天线、共存、controller bit-exact；
- 外部或加密 ESP-NOW、跨设备 fabric、丢包/重试；
- Core2 legacy UIFlow `RUNTIME-03` normal-WDT 启动和应用帧；
- 物理硬件、声学、光学、电气以及物理 PSRAM/cache timing；
- 本次是 `virtual-device validation`，不是 physical hardware validation。

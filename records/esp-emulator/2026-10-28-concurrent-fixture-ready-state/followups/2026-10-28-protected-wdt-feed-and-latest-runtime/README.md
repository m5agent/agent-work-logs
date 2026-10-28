# ESP Emulator protected WDTFEED 修复与最新 runtime 三设备复测

- 日期：`2026-10-28`
- 结果：`PARTIAL`
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：继续复测 StopWatch、StickS3、Core2 的 UIFlow2 接口，并处理
  统一暴露的模型与测试基础设施问题
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`8e47c6ba`](https://github.com/m5agent/m5stack-esp-emulator/commit/8e47c6ba83c042398d767a8d56ff47c16b927181)
- 功能提交：[`a07f49b7`](https://github.com/m5agent/m5stack-esp-emulator/commit/a07f49b7a8b5e680a24faf08541c7329e7ced760)
- 环境：macOS arm64、Python 3.12、Device Service `/api/v1`、
  UIFlow2 `v2.5.3`、QEMU TCG virtual device；物理硬件未使用

## 结论

`0069` 修正 classic ESP32 TIMG 的 `WDTFEED` 写保护语义：feed 不再要求先
解锁 `WDTPROTECT`，配置寄存器仍保持写保护。补丁合同、reverse-check 和
QEMU 增量构建通过。

在包含该修复的 QEMU `7855…` 上，三台设备完成 system/shared、17 个设备组、
协议、ESP-NOW、audio、candidate 和 Device Service API 复测。没有发现新的
模拟器功能回归；本轮新增的 GCC 编译合同问题也已修复并由 Linux CI 验证。

normal-WDT 下 legacy Core2 仍于约 `17.2529 s` 发生 TG0 stage-1 reset，
原厂 startup UI、setup/REPL 和完整应用帧仍未完成，因此 `RUNTIME-03`
继续为 `OPEN`。stock HTTP、Modbus async 与 TLS epoch 缺陷也仍保留。

## 关键证据

- QEMU SHA256：
  `78555183d53318fc25bc8413300e928d35bbbc1305f9d9648e97a73d34ce63b1`
- `0069` SHA256：
  `53b6557f0db174d8b0a280f354fbba42152f8c2918edfaf27b71de65c9cd04a8`
- 三台 system runtime：各 `50 PASS + 1 STATE_PASS`
- 三台 shared corrections：各 `7/7`
- 设备组：StopWatch `6/6`、StickS3 `5/5`、Core2 `6/6`，无 retry
- sockets/MQTT/network/EzData：`23/23`、`42/42`、`14/14`、`17/17`
- requests/Modbus candidate：三台各 `2/2`、`50/50`
- TLS candidate：三台各 `5/5`
- Device Service API：`81` operations、`95` cases PASS
- platform tests：`1393` 项 `OK`，`1` skip
- GitHub CI
  [`40718871624`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40718871624)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：
  [`WDTFEED`](https://github.com/m5agent/m5stack-esp-emulator/blob/8e47c6ba83c042398d767a8d56ff47c16b927181/docs/evidence/2026-10-28-core2-timg-wdt-feed/README.md)、
  [最新三设备复测](https://github.com/m5agent/m5stack-esp-emulator/blob/8e47c6ba83c042398d767a8d56ff47c16b927181/docs/evidence/2026-10-28-three-board-uiflow2-latest-runtime/README.md)

## 文件

- [report.md](report.md)：根因、修复、执行和边界
- [run.json](run.json)：机器可读结果
- [evidence/summary.json](evidence/summary.json)：脱敏计数与哈希

## 未覆盖项

- Core2 legacy `RUNTIME-03` 的 startup UI、setup/REPL、稳定 normal-WDT
  应用运行；
- 外部/PMK 加密 ESP-NOW peer、跨设备 fabric、RF/timing；
- 显式 HCI BLE 与未准入 Modbus RTU/PPP 组合；
- Core2 完整 28 类 M5UI 文档方法矩阵；
- 所有物理显示、触控、声学、光学、RF 和电气验证。

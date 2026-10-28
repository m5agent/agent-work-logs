# ESP Emulator Core2 stock UIFlow2 BLE via native HCI

- 日期：`2026-10-29`
- 结果：`PASS`（限定 Core2 BLEUART NUS）/ `PARTIAL`（其它 stock BLE 范围）
- 工作类型：`code_change`
- 问题来源：三设备 UIFlow2 全接口复测中的 stock BLE timeout
- 源码版本：[m5stack-esp-emulator@2e2f4076](https://github.com/m5agent/m5stack-esp-emulator/commit/2e2f4076292ca9ed0bc55cf680e48e0ce91f5987)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

此前 Core2 stock BLE 被错误送入 `core2-unified`，且没有提供
`core2-native-hci` 所需 matching ELF，超时因此被写成 stock GATT
`BLOCKED_MODEL`。runner 修复后，同一 stock base 在 matching ELF 和
`core2-native-hci` profile 上完成三个独立 `ble-nus` session，每个
`8/8 PASS`。

peer 实际发现 `M5-CORE2-UNIFIED`、连接、发现 NUS service、订阅 TX
characteristic、写入 `M5_CORE2_UNIFIED`，并收到精确通知
`ACK:M5_CORE2_UNIFIED`。guest 同时通过 `any/read/readline/irq`、
close、deinit 和清理判定。

## 关键证据

- `evidence/peer-exchange-summary.txt`
- `evidence/summary.json`
- CI：[40768653826](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40768653826)

## 文件

- `report.md`：根因、runner 修正、验证与边界
- `run.json`：机器可读记录
- `evidence/`：脱敏 peer 交换和 machine summary
- `patches/`：不适用；修复位于测试/服务 runner
- `code/`：不适用；代码已随源码提交

## 未覆盖项

- StopWatch/StickS3 stock internal-controller BLE 仍未闭环，不能继承 Core2；
- Core2 `m5ble.Server.get_client` 仍有 stock SDK `set` indexing 错误；
- BLE pairing/security、RF、天线、共存、物理时序和真机为 `NOT RUN`；
- 本次是 `virtual-device validation`，不是 physical hardware validation。

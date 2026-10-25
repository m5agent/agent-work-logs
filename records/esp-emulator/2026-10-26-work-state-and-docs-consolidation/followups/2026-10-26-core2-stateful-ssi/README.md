# ESP Emulator Core2 stateful SSI batch and current-state reconciliation

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户要求完整整理代码和文档，并把后续 SSI、Flash/cache
  handoff、WiFi/BLE 与当前待办统一到同一事实源
- 源码版本：
  [m5stack-esp-emulator @ 3d75d30](https://github.com/m5agent/m5stack-esp-emulator/commit/3d75d30d3a745e9e58c1585e1fe75029015c67c4)
- Base commit：`5a004b24053bf791203083be4dfa426f971525a8`
- 环境：macOS arm64；Python 3.13；Node 22；QEMU `9.2.2` virtual Core2；
  physical hardware `NOT RUN`

## 结论

新增 `0036-ssi-transfer-buf.patch`，为通用 SSI 增加可选批量字节接口：
未实现 callback 的器件继续走原逐字节 `ssi_transfer`；m25p80 只在
`STATE_READ` 使用快速路径，command/address/dummy/CS/地址回绕仍由原状态机
处理；ESP32 SPI 只在 receive-only data phase 使用批量接口。

前 512 个 64-byte 批次与原逐字节路径一致，bytes mismatch 为 `0`。重建
QEMU 后，Core2 UIFlow2 设备组与共享控制器完整 UIFlow2 矩阵均通过。相同
legacy `UIFlow_Core2` 固件在正常 WDT 下仍出现 interrupt-WDT/reset；关闭
WDT 的观察窗口也未到 setup/REPL，因此 `0036` 是有效数据面优化，但不是
`RUNTIME-03` 关闭证据。

直接 state trace 观察到 flash-operation can-start/complete 与 cross-core
reason 反复在 `0/1` 间变化，先前“cross-core 永久死锁”的判断撤回。当前
首要假设是大量同步 Flash/cache/DPORT handoff 的累计吞吐不足，需要把两核
PC、handoff、batch 与 watchdog feed 放到同一虚拟时间轴继续定位。

## 关键证据

- patch clean-base forward/reverse apply check：PASS；
- SSI 字节等价：`512` 个 `64-byte` 批次，`0` mismatch；
- Core2 UIFlow2 定向：`6/6` cases、`24/24` checks、零 retry；
- 共享控制器完整矩阵：`67/67` cases、`274/274` checks、零 retry；
- 平台测试 `501/501`、docs `41/41`、QEMU profile `19/19`：PASS；
- Node SHA/upload、worker credential migration、compileall、Ruff `E9/F`、
  coverage、catalog、snapshot 与 diff check：PASS；
- CI：[40226918011](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40226918011)；
- legacy normal-WDT、WDT-disabled progress、非空应用帧与物理硬件仍为
  `FAIL`/`NOT RUN`。

## 文件

- `report.md`：改动、执行、验证、边界与回滚；
- `run.json`：机器可读结果；
- `evidence/core2-ssi-summary.json`：脱敏哈希、矩阵结果和验证摘要；
- `patches/0001-ssi-transfer-buf.patch`：可与产品仓库 `0036` 对照的 SSI
  批量数据面补丁。

## 未覆盖项

- legacy UIFlow 在正常 WDT、真实 SSI/m25p80 数据面下仍没有非空应用帧；
- cross-core、DPORT 与 watchdog 的同时间轴因果关系尚未量化完成；
- `Core2FactoryTest` 修复后仍未重跑；
- 完整矩阵只覆盖当前 UIFlow2 设备组，不是任意固件；
- 物理 SPI Flash、cache、PSRAM、timer、WDT、RF、电气和真机均 `NOT RUN`。

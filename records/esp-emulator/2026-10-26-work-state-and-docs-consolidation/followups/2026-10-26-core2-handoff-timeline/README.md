# ESP Emulator Core2 unified handoff timeline and current-document reconciliation

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户要求完整整理近期代码和文档，并清理没有结合后续
  WiFi/BLE、Core2、网络和固件审查工作的旧信息
- 源码版本：
  [m5stack-esp-emulator @ 8391958](https://github.com/m5agent/m5stack-esp-emulator/commit/839195866b9cbf82e4e6b0d1a4ed802ea5ce4b9e)
- Base commit：`3d75d30d3a745e9e58c1585e1fe75029015c67c4`
- 环境：macOS arm64；Python 3.13.15；Node 22.14.0；QEMU 9.2.2 virtual
  Core2；physical hardware `NOT RUN`

## 结论

新增默认关闭的 `0037-esp32-handoff-trace.patch`，把 cross-core、DPORT
cache、SSI、UART 和 TIMG watchdog 事件统一到 QEMU virtual time、CPU 和
guest-PC 时间轴。该 trace 不改变控制器行为，也不构成 `RUNTIME-03` 修复。

两次 normal-WDT 运行都在最后一次 TG1 feed 后恰好 `800 ms` 进入 stage-0
timeout；canonical run 在 `2.4 s` 后记录 stage-1，replicate 在
`-no-reboot` 对照中停在 stage-0。WDT-disabled `sample=1024` 与
trace-off 的 507-byte banner-only Serial SHA 相同。1 ms PC 采样对照仍保持
固定 800 ms gap，但会扰动调度并更早 reset；最终 800 个样本只落在
CPU0 UART RX ISR 指令簇和 CPU1 MicroPython VM。该窗口没有 UART register
event，因此只能把中断/服务饥饿列为候选，不能写成 UART storm 根因。

当前 trace-off 回归为 Core2 UIFlow2 `6/6 cases`、`24/24 checks` 和完整
UIFlow2 `67/67 cases`、`274/274 checks`，均无 retry。同一 public
`UIFlow_Core2` 固件仍会在正常 WDT 下 reset PC `0`、保持黑帧且没有非空
应用帧，所以整体结果仍是 `PARTIAL`。

本轮同时修正了旧 patch 文档的过强承诺：`0003` 快照已经包含后续 PCM 状态，
`0004` 不能在当前 `0003` 后干净重放，且部分文件只存在于 retained target
tree。`0037` 因此明确标为 `0036` 后目标树的前序绑定补丁，不是裸上游
standalone patch。

## 关键证据

- normal-WDT：stage-0 feed gap 为 `800,000,000 ns`；canonical feed count
  `12,087`，replicate `12,045`；两次 timeout PC 不同；
- WDT-disabled：`sample=1024` 与 trace-off 同为 507 bytes，SHA
  `e996276519b4f8882739ff1c494dcecba313c99278857a53a984c1c9986a1b62`；
- PC control：800 samples、6 个 CPU0/CPU1 PC 对、窗口内只有 3 个 TIMG
  event、无 UART register event；本地 ELF 符号化明确未绑定 public BIN；
- 回归：Core2 `6/6`、完整 UIFlow2 `67/67`、平台 `504/504`、docs
  `41/41`、QEMU profile `19/19`；
- Node SHA/upload、worker credential migration、compileall、Ruff `E9/F`、
  coverage、catalog、profile、snapshot 与 diff check：PASS；
- patch predecessor forward/reverse apply check：PASS；
- CI：[40234012879](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40234012879)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS。

## 文件

- `report.md`：背景、改动、执行、验证、边界和回滚；
- `run.json`：机器可读结果；
- `evidence/core2-handoff-evidence.json`：脱敏 trace、Serial、回归和分类；
- `evidence/pc-symbolization.json`：未绑定 public BIN 的本地 ELF 符号；
- `patches/0001-esp32-handoff-trace.patch`：与产品仓库 `0037` 相同的前序绑定
  diagnostic patch。

## 未覆盖项

- legacy `UIFlow_Core2` 正常 WDT 应用启动仍 `FAIL`；
- CPU0 最后 800 ms 服务饥饿的 guest 根因仍未定位；
- `Core2FactoryTest` 修复后仍未重跑；
- 物理 cache/PSRAM、Flash timing、timer/WDT、bit-exact BT controller、
  RF、电气和真机均 `NOT RUN`；
- 完整 QEMU patch 系列没有恢复成从裸上游一键重建的 clean-room bootstrap。

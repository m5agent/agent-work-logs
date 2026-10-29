# M5Stack ESP Emulator Core2 TIMG watchdog feed rescheduling

- 日期：`2026-10-30`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator@91dca3a6`
- 环境：macOS Apple Silicon、Python 3.12、Device Service `/api/v1`、QEMU virtual Core2

## 结论

`0091-esp32-timg-feed-reschedule.patch` 修正 classic ESP32 TIMG watchdog
stage timer 的替换语义：成功 `WDTFEED` 后使用 `timer_mod_ns()` 安排新
deadline，不再使用会保留更早 pending deadline 的
`timer_mod_anticipate_ns()`。

同一 normalized legacy firmware 的 `runtime=qemu-wifi` 8 秒虚拟时点得到
`320x240`、`3,651` nonblack pixels、`36` colors 的 live frame。长窗仍在
约 `15.56 s` 触发 TG0 stage-1 reset，因此本记录只关闭 watchdog timer
replacement 子问题；factory UI、REPL、稳定应用帧和 `RUNTIME-03` 仍
`OPEN`。

## 关键证据

- 固件：normalized Flash SHA256
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- 诊断 QEMU：`7d03bb183a34cbbf8960a75e95703f92c2fec7fe6e14dad98707e9431caf83a4`
- Patch SHA256：
  `37823151abe23187f25100f7ff82f2642eaec2bc6a82548a40dd05c2b084c964`
- Frame SHA256：
  `35aedd447284a3e812e6cd9bec3e3167559a50f2c121eb43482dcfc7ab108fcc`
- 平台回归：`1583 OK + 1 skip`
- Patch forward/reverse check、protected-feed 和 status/CAS 契约通过

## 文件

- `report.md`：根因、改动、执行、证据和边界
- `run.json`：机器可读摘要
- `evidence/verification.summary.json`：脱敏验证摘要
- `patches/0001-esp32-timg-feed-reschedule.patch`：最小修复

## 未覆盖项

- factory startup UI、REPL/setup 和稳定应用帧
- physical hardware、物理 watchdog/cache/PSRAM timing、电气和 RF

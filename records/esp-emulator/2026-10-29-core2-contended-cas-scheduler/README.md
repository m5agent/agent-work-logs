# ESP Emulator Core2 contended-CAS scheduler attribution

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator@fe7770b4ea86a0faae8a40458df8a0dcd6a4fbff`
- 环境：macOS Apple Silicon；Core2 UIFlow2 QEMU；Device Service `/api/v1`

## 结论

同一 QEMU binary 的 A/B 证明，单线程 TCG 默认 `100 ms` RR quantum 会
显著放大 Core2 跨核 spinlock 等待。候选 `0088` 在真实 failed cross-core
S32C1I 后只缩短下一个 RR quantum 到 `1 ms`，5 秒 WDT-off A/B 将
S32C1I/contended 操作从 `1,070,625/984,964` 降到 `91,465/2,702`，
episode time 从 `2.239772672 s` 降到 `1.017736288 s`。

候选没有关闭 `RUNTIME-03`。normal WDT 仍在约 `17.248 s` 触发
`TG0WDT_SYS_RESET`，startup UI、setup/REPL 和非空应用帧均未达到。

## 关键证据

- public firmware source SHA256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`
- QEMU SHA256：
  `75e7fa97424c859c6e1fe918dda203aa2c6509e9c81937893a15d2a4a46b6714`
- patch：`0088-xtensa-contended-cas-fair-yield.patch`
- patch SHA256：
  `f3fbb89c9aa86922f27d236915cc268a65832df4e0c25e85b0fa451beae9aa48`
- 5 秒 control/candidate SSI `0x05`：`2,078/2,086`
- 5 秒 control/candidate SSI `0xBB/64`：`2,386/2,394`
- normal-WDT control/candidate reset：
  `17.249535709 s / 17.248020126 s`
- platform regression：`1560 OK, 10 skipped`
- PR #40 已合并，merge commit：
  `c0aeb619fa3fe1fe8e12a43c49ac22d7f2135eca`

## 文件

- `report.md`：调度边界、A/B、量子调参和启动边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：机器摘要
- `evidence/same-binary-ab.txt`：5 秒同 binary A/B
- `evidence/normal-wdt.txt`：normal-WDT reset 对照

## 未覆盖项

这只是 `virtual-device validation`。physical hardware、真实 RF、cache/PSRAM
timing、电气和长期稳定性均为 `NOT RUN`。`RUNTIME-03` 的 startup UI、
setup/REPL、非空应用帧和 normal-WDT 稳定运行仍为 `OPEN`。

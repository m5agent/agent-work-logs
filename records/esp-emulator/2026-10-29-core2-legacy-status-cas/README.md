# ESP Emulator Core2 legacy status/CAS 关联诊断

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：[m5stack-esp-emulator](https://github.com/m5agent/m5stack-esp-emulator) `RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator @ 66af02cc6061bded00659ee13632f5e3a9a397dc`
- 环境：macOS arm64、Python 3.12、QEMU `d60e6fb0…`、`runtime=qemu-wifi`、`icount shift=5`

## 结论

`0075` 将 legacy Core2 的 `RDSR(0x05)` 返回状态、前序 `0xBB/64`
读、cache counter 变化、PS/IRQ 与有界 `s32c1i`
PC/caller/lock/old-owner/holder-PC 聚合输出到显式 freeze。

WDT-off 20 秒窗口内 status bit0（WIP/BUSY）始终为 `0`，主要 gap
仍位于 64-byte read 后、下一次 status read 前。CAS 汇总显示
`0x3ffbf2cc` 上的真实跨核 scheduler/list 锁竞争，而不是 Flash busy
位或异常 old-owner 值。normal-WDT 与 failed-CAS TCG-slice-yield
都在约 `17.249 s` 触发同一 TG0 stage-1 reset，因此后者被否定为修复。

`RUNTIME-03` 保持 `OPEN`；没有 legacy matching ELF/MAP，未把
BIN-bound PC 命名成精确函数。

## 关键证据

- `RDSR`：`12,093`；`0x00=4,278`、`0x02=7,815`；bit0 置位数 `0`
- status gap：`17.074056543 s / 20 s`，占 `85.370%`
- `s32c1i`：`6,288,123` 次，`5,737,336` 次真实跨核竞争
- 主要锁：`0x3ffbf2cc`，`5,482,913` 次 CAS、`253,241` 次成功
- normal-WDT first reset：`17.248490561 s`
- failed-CAS yield first reset：`17.248930720 s`
- serial：只有 MicroPython banner，无 REPL prompt
- frame：302-byte black PNG，SHA256 `57580743…`
- 平台测试：`1432 OK, 1 skip`
- CI：[40783815160](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40783815160) 两个 job PASS

## 文件

- `report.md`：完整调查、实现、负向控制和边界
- `run.json`：结构化结论与检查项
- `evidence/summary.json`：机器摘要
- `patches/0001-esp32-legacy-status-cas-correlation.patch`：`0075` patch
- `code/README.md`：复现入口和源码位置

## 未覆盖项

物理硬件、RF、电气、物理 cache/PSRAM timing 和真机行为均 `NOT RUN`。
当前状态/来源是 virtual-device validation；`RUNTIME-03` 的 startup UI、
setup/REPL、非空应用帧和 normal-WDT 启动仍未闭环。

# ESP Emulator Core2 IPC/flash handoff stack attribution

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator@c4bd55344b2aae72045cdb530f278f7806598c70`
- 环境：macOS Apple Silicon；Core2 UIFlow1 QEMU；本地 Device Service `/api/v1`

## 结论

三次同固件、同 QEMU、normal-WDT 的 `17.200000 s` bounded-stack freeze
都将 CPU0 定位在 BIN `0x40087980..8e` 的
`spi_flash_op_block_func` complete-flag 等待循环；CPU1 三次位于不同
IPC/队列/调度启动路径，说明这不是双核永久 deadlock。

同时修正了一个采样误读：默认 handoff trace 每 1024 个 routine event 才保留
一条，不能把采样后的 `transaction-begin/end` 当成同一事务。runner 现在显式
支持 `--trace-sample`；2 秒全量控制得到 13 对同步 `0 ns` 事务，排除“单个短
Flash 命令事务耗时约 0.4 秒”的解释。

该里程碑没有修复 `RUNTIME-03`。normal WDT 仍在 BOARD/APIKEY 前 reset，
startup UI、setup/REPL、非空应用帧和物理硬件仍未通过。

## 关键证据

- public firmware SHA256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`
- QEMU SHA256：
  `75e7fa97424c859c6e1fe918dda203aa2c6509e9c81937893a15d2a4a46b6714`
- CPU0 stable registers：`A0=0x80088a31`、`A9=0x3ffc7ec8`、
  `A12=0x3ffbf2cc`
- CPU0 stable stack frames：`0x400889c4`、`0x40087950`、
  `0x800840a0`
- 三次 CPU1 PC：`0x40084312`、`0x4008448a`、`0x40095c5c`
- 三次 serial：507 bytes，SHA256
  `e996276519b4f8882739ff1c494dcecba313c99278857a53a984c1c9986a1b62`
- full-trace control：13 begin、13 end、13 对 `0 ns`
- platform regression：`1560 OK, 10 skipped`
- PR #41 已合并，merge commit：
  `3e424ee83567a7813f4d8862b24323a4cd500152`

## 文件

- `report.md`：冻结栈、IPC source-shape、采样控制和验证边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：机器摘要
- `evidence/three-freeze-stacks.txt`：三次 CPU/frame/serial 摘要
- `evidence/full-trace-control.txt`：trace-sample 对照摘要
- [`followups/2026-10-29-handoff-episode-budget/`](followups/2026-10-29-handoff-episode-budget/)：`0089` icount-safe trace 与两次 50 秒 handoff 预算

## 未覆盖项

这只是 `virtual-device validation`，不是 `RUNTIME-03` 修复。没有 matching
private legacy ELF/MAP，函数名仅为 BIN/source-shape 匹配；physical hardware、
真实 cache/PSRAM timing、电气和长期稳定性均为 `NOT RUN`。

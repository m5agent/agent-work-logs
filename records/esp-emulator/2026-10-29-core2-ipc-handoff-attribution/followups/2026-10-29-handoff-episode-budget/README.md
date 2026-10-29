# ESP Emulator Core2 flash handoff episode budget

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator@7e52d6301f647e893995ea71e4bf9dc24722d271`
- 环境：macOS Apple Silicon；Core2 UIFlow1 QEMU；本地 Device Service `/api/v1`

## 结论

`0089` 修复 BIN-bound PC trace 在 no-I/O translation block 中读取虚拟时钟
导致的 `Bad icount read`。修复后两次独立 50 秒 wall-time normal-WDT 运行
都到达既有 TG0 reset。

每次 reset 前约发生 `12.6k` 个完整 flash/cache handoff。CPU0
`spi_flash_op_block_func` 累计等待约 `9.83-9.85 s`，占约 57% reset
预算；单次最大只有约 `6.7-6.8 ms`。因此当前不存在一个可继续追的长
handshake deadlock，剩余方向是正常 handoff 的高频累计成本。

该结果没有修复启动：两次都没有 `BOARD NAME`、`APIKEY`、setup/REPL，
frame 仍是同一 302-byte 黑帧。`RUNTIME-03` 保持 `OPEN`。

## 关键证据

- normalized firmware SHA256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`
- fixed QEMU SHA256：
  `7d9b1f43ecc5a9b842c370dd52981ae7eab1c71e996f5dbf26a61bb3b2c0f353`
- patch：`0089-xtensa-handoff-pc-trace-io-boundary.patch`
- patch SHA256：
  `14326ad71d3c93ee564173387bba6b6efc38b61f24830e363134261e8e2b0dde`
- block wait：
  `9.851852864 / 9.828771008 s`
- handoff count：`12,645 / 12,693`
- largest single wait：`6.655552 / 6.781792 ms`
- platform regression：`1562 OK, 10 skipped`
- PR #42 已合并，merge commit：
  `37480e9fc7a3f53db0fa8dbbdc9438d37ef1d5af`

## 文件

- `report.md`：诊断修复、phase 配对、两次执行和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：两次运行的机器摘要
- `evidence/episode-runs.txt`：reset、wait、frequency 和 serial 摘要

## 未覆盖项

仅 `virtual-device validation`。物理 cache/Flash timing、电气、RF、
startup UI、setup/REPL、非空应用帧和真机均 `NOT RUN`/`OPEN`。

# ESP Emulator Core2 legacy SSI command correlation

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：继续定位 Core2 legacy `RUNTIME-03` 的 SSI 请求与等待来源
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`19651bf0`](https://github.com/m5agent/m5stack-esp-emulator/commit/19651bf0cb521ab1e1dbb102895c3bb2578b4f5d)
- 环境：macOS arm64、隔离 Device Service `/api/v1`、Core2 QEMU
  `qemu-wifi`、`icount shift=5`；物理硬件未使用

## 结论

新增 `0072-esp32-ssi-command-correlation.patch`，在 `0071` 上增加
command-length 联合键、per-command gap 和 command transition。三张表都是
有界稀疏表并带 overflow 计数；本轮的联合、per-command 和 transition 计数
分别严格等于 transaction 或 `transaction-1`，overflow 全为 `0`。

同 SHA 的 80 秒 WDT-off 控制得到：

- `105,346` transactions；
- `0x05/1` 为 `50,071`；
- `0xBB/64` 为 `49,882`；
- `0xBB/64 -> 0x05/1` 为 `49,582`；
- `0x05/1 -> 0xBB/64` 为 `49,600`；
- `0x05` 前 gap 占 `82.398%`，平均 `1.3115489 ms`；
- `0xBB` 前 gap 占 `0.191%`，平均约 `3.05 us`。

这确认 guest 在主循环中交替执行 64-byte Fast Read 与 1-byte RDSR。主要
预算位于 64-byte read 之后、下一次 status read 之前，而不是 controller
收到 status command 后的单次操作。

新 QEMU 的 normal-WDT 仍在 `17.249440926 s` 首次 reset，TG1 零 timeout，
说明 instrumentation 未改变失败边界。`RUNTIME-03` 仍为 `OPEN`。

## 关键证据

- QEMU SHA256：
  `4aa418e6cba1a6d7104906ff88991c62c85e02661fa6ba4e256743f13b6753ba`
- Patch SHA256：
  `107cc478b2a4157d391d6d3331a141683ee61ed37d06ba81244afb92324fa024`
- Firmware SHA256：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- WDT-off evidence SHA256：
  `eb99b870d2bb60cf01bd1e5864345c853ffa267b45fffbf72945721a70d635e9`
- normal-WDT evidence SHA256：
  `d69e8a4b90aeecc13174024e6fd9dfe0d7337d4e3f45e5a611fcc9dbf9c6f007`
- Platform tests：`1411` 项 `OK`，`1` skip
- GitHub CI
  [`40757438108`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40757438108)
  两个 job 均 PASS
- 主仓证据：
  [SSI command correlation](https://github.com/m5agent/m5stack-esp-emulator/blob/19651bf0cb521ab1e1dbb102895c3bb2578b4f5d/docs/evidence/2026-10-29-core2-ssi-command-correlation/README.md)

## 文件

- [report.md](report.md)：联合分布、gap 归因和 normal-WDT 控制
- [run.json](run.json)：机器可读结果
- [evidence/summary.json](evidence/summary.json)：脱敏直方图和哈希

## 未覆盖项

- `0x05` 前约 `1.31 ms` gap 内的 guest PC/driver/IRQ 归因；
- matching `UIFlow_Core2 v1.15.4` source/ELF/MAP；
- startup UI、setup/REPL、非空应用帧；
- 物理 Flash/cache、RF、电气和硬件时序。

# ESP Emulator Core2 legacy pre-boot phase profile

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：`RUNTIME-03` pre-boot guest/controller 工作预算
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`419235e9`](https://github.com/m5agent/m5stack-esp-emulator/commit/419235e91d9a8e687e63fc9c422b91d1b0cc76ea)
- 环境：macOS arm64、隔离 Device Service `/api/v1`、Core2 QEMU；
  物理硬件未使用

## 结论

修复了 `run_pause_sweep.py` 的可观测性缺口：PC sampling 与 UART trace
现在由显式参数启用并写入 evidence 元数据，snapshot 同时汇总 PC 热点和
sampled SSI read cadence。

最新 80 秒 WDT-off phase profile 把 Core2 legacy pre-boot 工作收敛到
约十万次小块 SSI read：

- banner `2.7724 s`；
- BOARD NAME `54.9924 s`；
- APIKEY `54.9971 s`；
- `boot.py` start/done `77.8622/78.3712 s`；
- SSI `103,058` transactions、`3,181,984` RX bytes；
- CPU0 `0x4026306e` waiti 形态 `31.0%`；
- CPU0 `0x40087980..8e` BIN-bound handoff 簇 `60.4%`。

同固件 normal-WDT 仍在 `7.2536 s` stage-0、`17.2536 s` stage-1 reset，
早于 BOARD NAME。`RUNTIME-03` 仍为 `OPEN`；这次没有产品修复。

## 否定控制

四类立即切核实验均执行后丢弃：

- 所有 high-priority memw/retw 立即退出 TB；
- 仅 CPU1 handler 首次立即退出；
- cross-core 写时退出当前 TB；
- SPI `TRANS_DONE` 时退出当前 TB。

它们分别导致宿主开销上升、虚拟时间推进变慢或 TG1 被饿住，没有改善
BOARD/APIKEY 或 normal-WDT 启动预算。

## 关键证据

- Firmware normalized SHA256：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- QEMU SHA256：
  `fccfa931c032f8cae6b90e97ba5f98b1770fbf6856446c4db5f7950241e1fe90`
- WDT-off QEMU stderr SHA256：
  `8e12e54a4a4e74cef831720c9ee305f549a6547321e3891ed9a1939fc84de780`
- 平台测试：`1400` 项 `OK`，`1` skip
- CI
  [`40732335677`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40732335677)
  两个 job 均 PASS
- 主仓证据：
  [Core2 pre-boot phase profile](https://github.com/m5agent/m5stack-esp-emulator/blob/419235e91d9a8e687e63fc9c422b91d1b0cc76ea/docs/evidence/2026-10-29-core2-preboot-phase-profile/README.md)

## 文件

- [report.md](report.md)：实验、时间线、否定控制和边界
- [run.json](run.json)：机器可读结果
- [evidence/summary.json](evidence/summary.json)：脱敏摘要和哈希

## 未覆盖项

- 64-byte read cadence 来自 guest driver 还是缺失的 controller/DMA bulk path；
- SPI completion 到下一 host command 的精确虚拟时间归属；
- matching `UIFlow_Core2 v1.15.4` ELF/MAP；
- legacy startup UI、setup/REPL、非空应用帧；
- 物理 Flash/cache、PSRAM、RF、电气和硬件时序。

## 后续

- [SSI transaction profile](followups/2026-10-29-ssi-transaction-profile/)：
  `0071` 增加完整 command、RX-length 和 command gap 聚合，确认约五万组
  `0x05` 与约五万组 `0xBB/64B`，并把主要预算定位到 guest 两次 command
  之间。

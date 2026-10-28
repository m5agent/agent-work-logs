# ESP Emulator Core2 legacy SSI transaction profile

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：继续处理 Core2 legacy UIFlow `RUNTIME-03` 的 pre-boot
  SSI transaction 分布
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`80b2ae15`](https://github.com/m5agent/m5stack-esp-emulator/commit/80b2ae1575ffd8cc66404edb96c3e4342be02225)
- 环境：macOS arm64、隔离 Device Service `/api/v1`、Core2 QEMU
  `qemu-wifi`、`icount shift=5`；物理硬件未使用

## 结论

新增 `0071-esp32-ssi-transaction-profile.patch`，在默认关闭的 handoff
metrics 中保存完整 16-bit command、RX-length 和
completion→next-command gap 聚合，并只在显式 freezes 输出。runner 会验证
command 总数、RX-length 总数和 gap 总数与 transaction 计数严格一致。

同一 `UIFlow_Core2 v1.15.4` 固件的 WDT-off 80 秒控制得到稳定请求序列：

- `104,302` transactions；
- `0x05` RDSR `49,489`；
- `0xBB` Dual-I/O 64-byte Fast Read `49,586`；
- RX length `1` `53,054`、`64` `49,586`；
- `104,301` 个 command gap 合计 `79,699,109,375 ns`；
- gap 主要分布在 `1-10 us`、`100 us-1 ms` 和 `1-10 ms`。

开启 PC sampling 的独立控制与无采样结果相近，排除采样本身制造该请求
形态。新 QEMU 的 normal-WDT 仍在 `17.253695649 s` 首次 reset，TG1 零
timeout，说明 instrumentation 没改变 `RUNTIME-03` 边界。

当前结论：约十万次小 transaction 是 controller 边界真实收到的 guest
command 序列，约 `79.7/80 s` 位于相邻 command 之间；尚未命名具体 guest
driver/IRQ 路径，也尚未关闭 startup UI/应用帧。

## 关键证据

- QEMU SHA256：
  `fbc2850c924d535d6c3a2c5dedf5772fec403da6e36ccecf20d811de1cf81fbe`
- Patch SHA256：
  `3c53c5a74128891988d73addfed710c865f094b188a30be47f661beca72afc6c`
- Firmware SHA256：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- 无采样 WDT-off evidence SHA256：
  `918ee740d3e9b819e0ac61a4c258db20da5a62b5649f9c9a20101f2d32ccd244`
- 有采样 WDT-off evidence SHA256：
  `43c92ca1a0ed764bcfd5305fc4690e1f22317680b0684744e4beb1cfcb25ea44`
- normal-WDT evidence SHA256：
  `ee1c33f403d7b71ef186d0d4d83494f487f258da906d41a6fe062b64b974bf9e`
- Platform tests：`1409` 项 `OK`，`1` skip
- GitHub CI
  [`40754517125`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40754517125)
  两个 job 均 PASS
- 主仓证据：
  [SSI transaction profile](https://github.com/m5agent/m5stack-esp-emulator/blob/80b2ae1575ffd8cc66404edb96c3e4342be02225/docs/evidence/2026-10-29-core2-ssi-transaction-profile/README.md)

## 文件

- [report.md](report.md)：改动、三个控制、结果和边界
- [run.json](run.json)：机器可读结果
- [evidence/summary.json](evidence/summary.json)：脱敏直方图和哈希

## 未覆盖项

- command-length 联合键与按 command 的 gap；
- 反复执行 `0x05`/`0xBB` 的具体 guest driver 和 interrupt-delivery 路径；
- matching `UIFlow_Core2 v1.15.4` source/ELF/MAP；
- startup UI、setup/REPL、非空应用帧；
- 物理 Flash/cache、RF、电气和硬件时序。

## 后续

- [SSI command correlation](followups/2026-10-29-ssi-command-correlation/)：
  `0072` 确认 `0xBB/64 -> 0x05/1 -> 0xBB/64` 主循环，并将 `82.4%`
  gap 定位到下一次 status read 前；具体 guest driver/IRQ 路径仍开放。

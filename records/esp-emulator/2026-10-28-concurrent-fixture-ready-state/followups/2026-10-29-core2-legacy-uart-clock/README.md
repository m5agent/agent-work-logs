# ESP Emulator Core2 legacy UART 与虚拟时钟对齐

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change` + `virtual_device_validation`
- 问题来源：继续处理 Core2 legacy UIFlow `RUNTIME-03` 的 normal-WDT reset
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`5bf2d2e3`](https://github.com/m5agent/m5stack-esp-emulator/commit/5bf2d2e323bd8cc8d2b66218fb30939f27cbd5f6)
- 环境：macOS arm64、Device Service `/api/v1`、Core2 QEMU TCG、
  UIFlow_Core2 `v1.15.4`；物理硬件未使用

## 结论

新增默认关闭的 UART TX 虚拟时间戳并让状态 runner 将逐字节输出重组为完整
串口行。WDT-off 80 秒 evidence 首次把 boot marker、SSI/DPORT handoff 和
WDT 放到同一时间轴：

- MicroPython banner 于 `2.7724 s` 完成；
- `BOARD NAME`/`APIKEY` 于 `54.995/55.002 s`；
- 用户 `boot.py` start/done 于 `77.109/77.615 s`；
- normal-WDT 仍在 `17.2529 s` 触发 TG0 stage-1 reset。

显式 `shift=2` 在更长墙钟窗口中仍在 `15.5609 s` reset，serial 未到
BOARD NAME。说明降低 accelerator 不改变该 watchdog gate，不能作为产品
修复。`RUNTIME-03` 继续保持 `OPEN`。

## 关键证据

- QEMU SHA256：
  `f0eb5f6c26f82ce99d6dad4006fcd0748991ba1a8d1ce780092d57d01d8e798e`
- `0070` SHA256：
  `43e7771613dd4a1dbcb66056961ed8c6bfa496d6128b019b4113e5e9e989ea40`
- Firmware normalized Flash SHA256：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- 80 秒状态点：CPU0 `0x4008798e`、CPU1 `0x40095b31`；
  SSI `104,061` transactions、cross-core writes `432,918`；
- platform tests：`1398` 项 `OK`，`1` skip
- GitHub CI
  [`40723613353`](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40723613353)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：
  [UART 与虚拟时钟对齐](https://github.com/m5agent/m5stack-esp-emulator/blob/5bf2d2e323bd8cc8d2b66218fb30939f27cbd5f6/docs/evidence/2026-10-29-core2-legacy-uart-clock/README.md)

## 文件

- [report.md](report.md)：假设、执行、证据和边界
- [run.json](run.json)：机器可读结果
- [evidence/summary.json](evidence/summary.json)：脱敏时间线和哈希

## 未覆盖项

- 造成 pre-boot work budget 膨胀的具体 guest/controller 缺陷；
- matching legacy source/ELF/MAP；
- normal-WDT startup UI、setup/REPL 和非空应用帧；
- 外部/加密 ESP-NOW、物理硬件、RF、声学、光学和电气验证。

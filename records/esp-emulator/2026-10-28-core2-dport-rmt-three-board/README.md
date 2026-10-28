# ESP Emulator：Core2 DPORT/RMT 修复与三设备 UIFlow2 回归

- 日期：`2026-10-28`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：Core2 legacy UIFlow `RUNTIME-03` 与 StopWatch / StickS3 /
  Core2 UIFlow2 接口复测
- 源码版本：[`m5agent/m5stack-esp-emulator`](https://github.com/m5agent/m5stack-esp-emulator)
  @ [`805925d8`](https://github.com/m5agent/m5stack-esp-emulator/commit/805925d8336fac28652d5bddfa1df0ec4b1606b8)
- 环境：macOS arm64、`qemu-system-xtensa`、独立可见 Device Service lease；
  不记录内部端点或设备唯一标识

## 结论

本轮关闭两个独立的 Core2 模型缺口：

1. Xtensa level-4/5 DPORT handoff 在单线程 TCG icount 下会被大 slice 打乱，
   导致 CPU0 等 start、CPU1 等 end。`0065` 只在协议顺序点协作让出，五轮
   独立首启动 `5/5 PASS`。
2. classic ESP32 RMT 缺失使 legacy Neopixel translator 读到
   `conf0.mem_size=0` 并报 `OSError`。`0066` 补齐寄存器、RMTMEM、
   threshold、`TX_END` 和 INTMATRIX 后，Serial 到达 `BOARD NAME`/`APIKEY`。

最终 QEMU
`2026673273b5bced2c2696ac4850a48f5ea47d8e9c80d6ceb2cf15f68c36d29f`
在 StopWatch、StickS3、Core2 上完成并发 UIFlow2 回归：system runtime
各 `50 PASS + 1 STATE_PASS`，shared corrections 各 `7/7`，设备组
StopWatch `6/6`、StickS3 `5/5`、Core2 `6/6`，17 个组 case 全部首轮
PASS、无 retry。

`RUNTIME-03` 仍不能关闭：normal WDT 仍在约 `17.25 s` 触发
`TG0WDT_SYS_RESET`；WDT-off 68 秒控制到达 `APIKEY`，但帧仍是 302-byte、
0 nonblack pixels。display completion、`lv_disp_flush_ready`、setup/REPL
和非空应用帧仍未出现。

## 关键证据

- build/runtime：QEMU hash 见 `evidence/platform-checks.json`；
- Core2 serial：`evidence/core2-serial-summary.txt`；
- RMT TX：`evidence/core2-rmt-summary.txt`；
- legacy late frame：`evidence/core2-black-frame.png`；
- 三设备与运行时摘要：`evidence/runtime-and-regression-summary.json`；
- 设备组哈希和计数：`evidence/three-board-results.json`；
- 主仓证据：
  [`2026-10-28-cooperative-highint-rmt`](https://github.com/m5agent/m5stack-esp-emulator/blob/805925d8336fac28652d5bddfa1df0ec4b1606b8/docs/evidence/2026-10-28-cooperative-highint-rmt/README.md)。

## 文件

- `report.md`：根因、改动、执行、边界与回滚
- `run.json`：机器可读摘要
- `evidence/`：脱敏运行摘要和黑帧
- `patches/`：固定 commit patch 链接、base ordering 和 reverse-check 说明
- `code/`：不适用；可重建测试位于主仓

## 未覆盖项

- physical hardware、RF、电气、声学和光学：`NOT RUN`；
- legacy normal-WDT 非空应用帧、display completion、setup/REPL：`OPEN`；
- RMT GPIO waveform、全生命周期和 Neopixel 光学：`NOT MODELED`；
- matching public legacy ELF/MAP：`NOT RUN`；
- Core2 28 类 M5UI 完整文档方法矩阵与 ESP-NOW payload：仍为既有边界。

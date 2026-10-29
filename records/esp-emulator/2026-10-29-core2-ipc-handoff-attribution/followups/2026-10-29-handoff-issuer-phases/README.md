# ESP Emulator Core2 handoff issuer and IPC phases

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03`
- 源码版本：`m5agent/m5stack-esp-emulator@efb74d6f06692e4dc274d144d91c18ced2ac9300`
- 环境：macOS Apple Silicon；Core2 UIFlow1 QEMU；本地 Device Service `/api/v1`

## 结论

issuer 关联证明正常 handoff 的固定成本与 64-byte Flash 数据量无关：

- `6,806` 个 episode 各包含一条 `0x40093b57` fast-read issuer 和一条
  `0x4006222c` status issuer，平均等待 `860.591 us`；
- `1,342` 个 episode 完全不含这两类 issuer，平均仍为 `888.354 us`；
- 仅 status read 的 `48` 个 episode 平均 `894.786 us`。

initiator phase split 进一步显示，`1,974` 个 episode 中
`0x40087a25 -> 0x40087a31` 的 IPC 往返 source shape 平均耗时
`615.595 us`。可观测的 poll、priority、两级 cache-disable 和 Flash work
都明显更小，因此下一目标应是跨核 IPC wakeup/handoff 延迟，而不是 Flash
命令或 64-byte 数据面。

`100 us` contended-CAS RR quantum 和临时 `can_start` immediate-yield
均未改善，已丢弃。正常 WDT、startup UI、setup/REPL、非空应用帧和真机仍未
通过，`RUNTIME-03` 保持 `OPEN`。

## 关键证据

- firmware SHA256：
  `18d77e28adfacf7e719a167bd0c3450b78357d13cb1d2f2a8b7bccc2248a909a`
- issuer-correlation QEMU：
  `7d9b1f43ecc5a9b842c370dd52981ae7eab1c71e996f5dbf26a61bb3b2c0f353`
- phase-split QEMU：
  `d14e31e1270e2f42be44a46af2b3bc3c84ffa342ce83edcb424e123769922b27`
- PR #44 merge：
  `3788aeaedc7de9566ac45a15092f133122f82d8a`

## 文件

- `report.md`：episode 分组、initiator phases、负控和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：机器摘要
- `evidence/issuer-groups.txt`：episode 分组与 phase 数据

## 未覆盖项

所有名称均为 BIN-bound source shape；physical cache/Flash timing、电气、
startup UI、REPL、非空帧和真机 `NOT RUN`/`OPEN`。

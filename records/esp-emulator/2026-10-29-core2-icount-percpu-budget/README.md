# ESP Emulator Core2 per-vCPU icount fairness budget

- 日期：`2026-10-29`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-03`，PR
  [#45](https://github.com/m5agent/m5stack-esp-emulator/pull/45)
- 源码版本：
  `m5agent/m5stack-esp-emulator@5817ce8b`
- Merge：
  `ed612f3b1589221dfdbad9e067cebafc7d231d8a`
- 环境：macOS Apple Silicon；Core2 QEMU；Device Service `/api/v1`

## 结论

新增 `0090-icount-percpu-fairness-cap.patch`，为 multi-vCPU deterministic
`-icount` 增加 per-vCPU virtual-time budget cap。Core2 默认使用 `10 us`，
可通过 `M5_CORE2_ICOUNT_MAX_PERCPU_NS=0` 恢复 uncapped control。

同一 public legacy 固件、normal WDT、`qemu-wifi` 和 trace 路径 A/B：

- CPU1 initiator `can_start -> IPC return` mean：
  `563.667 us -> 56.249 us`；
- peer Flash block wait mean：
  `728.443 us -> 184.689 us`；
- callback return 到下一次 prepare mean：
  `181.869 us -> 34.074 us`。

该结果关闭“双 vCPU icount 固定调度预算放大了正常 IPC handoff”这一子问题。
最终 QEMU 的 Core2 UIFlow2 设备组全部 PASS，platform 为
`1574 OK + 1 skip`。

## 关键证据

- firmware SHA256：
  `4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- QEMU SHA256：
  `568079f3b9e818ef1cc29b9e7cd1c5c036af19196668a12174ed79ec96c262ed`
- patch SHA256：
  `4c122ab3722c8fa17f9a518c51863f5ff879bd84afb9c78b2ca63516808245e7`
- normal-WDT capped long run：
  timeout `7.242815742 s`，reset `17.242875841 s`
- 最终 frame：302-byte black PNG，
  `57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`

## 文件

- `report.md`：根因、改动、A/B 和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：机器可读摘要

## 未覆盖项

normal-WDT 仍在 BOARD/APIKEY 前 reset；serial 没有 BOARD NAME、APIKEY、
setup 或 REPL，frame 仍为黑帧。`RUNTIME-03`、startup UI、非空应用帧、
物理 cache/Flash timing 和硬件验证继续 `OPEN`/`NOT RUN`。

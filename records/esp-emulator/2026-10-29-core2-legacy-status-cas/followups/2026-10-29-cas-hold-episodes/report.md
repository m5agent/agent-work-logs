# Core2 legacy CAS hold intervals 报告

## 背景

前一轮 `0075` 已排除 Flash RDSR WIP/BUSY，并把主要 gap 收敛到 legacy
scheduler/list 跨核锁竞争。本轮目标是量化失败 CAS 形成的持锁 episode，
并判断 failed-CAS slice yield 是否能改变 normal-WDT reset。

## 结论

- 新增 `0086-esp32-legacy-cas-episode-profile.patch`。
- episode 按 CPU/lock 聚合失败 attempt、持续时间、最大 attempt gap 和最后
  holder CPU；桶数量固定，overflow 单独计数。
- normal-WDT 与 WDT-off 都显示长持有/等待区间，关闭 WDT 不会消除模式。
- failed-CAS slice yield 在 10 秒把 task-queue 等待降低，但 15 秒窗口把
  等待转移到 queue mux，总 episode 仍约 `5.384 s`。
- normal-WDT reset 边界没有变化，因此 yield 不是修复。

## 锁映射

`0x3ffbf2cc` 与 public legacy ESP-IDF v3.3.5 的 `xTaskQueueMutex`
指令/控制流匹配；主要 waiter 是 `xTaskIncrementTick` 和
`vTaskSwitchContext`。`0x3ffb7ab0` 对应某个 `Queue_t + 76` 的 mux。
这不是 matching application ELF/MAP 符号，不能把该映射描述成逐函数身份。

## 执行

- 环境：macOS arm64；`runtime=qemu-wifi`；exact-time freeze
- QEMU：`0a63c37f62752a3020988bb6b087b5eb11f4a6af323255f978ccb7012cb8be73`
- Flash：`4d2d648bd8707a1789d540366015a1b90dc816b66a04163048626ea29e333ed4`
- normal-WDT：`238` episodes / `9.316534114 s` / max `631 ms`
- WDT-off：`253` episodes / `7.825981502 s` / max `581 ms`
- 所有 session 均在停止前留 evidence，以 `purge=0` 保留 history。
- PR #37 与 merge commit main CI 的 platform/network jobs 均 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | patch 对 retained source reverse apply |
| transport | PASS | Device Service + QMP exact-time freeze |
| device_response | PASS | handoff/CAS trace 输出有界且 overflow 为 0 |
| data_behavior | PARTIAL | lock 类型与 waiter 已映射；无 matching ELF/MAP |
| visual_or_physical | NOT RUN | normal-WDT reset、黑帧、应用帧仍未解决 |

## 验证边界

本结果只增加诊断和归因证据。它不关闭 watchdog reset、display completion、
setup/REPL 或应用帧，也不证明 physical hardware、RF、电气或 cache/PSRAM
timing。

## 风险与回滚

诊断路径默认关闭，不改变 guest 指令或 CAS 结果。回滚 patch `0086` 即可
移除 episode profiling；不会影响既有 handoff trace 的默认行为。

# ESP Emulator Core2 contended-CAS scheduler attribution 报告

## 背景

- 来源：`RUNTIME-03`，PR
  [#40](https://github.com/m5agent/m5stack-esp-emulator/pull/40)。
- 现象：legacy UIFlow 在 pre-boot 阶段出现长 `xTaskQueueMutex` 等待和
  normal-WDT reset；既有 episode 诊断无法区分 host vCPU 调度放大与 guest
  真实长临界区。
- 目标：保持 guest CAS、icount 和 WDT 语义不变，单独测量单线程 RR quantum
  对跨核 spinlock 的影响，并验证是否足以解除启动失败。

## 结论

- 状态：`PARTIAL`（virtual-device validation）
- 根因贡献：默认 TCG `thread=single` 让 vCPU 一次运行约 `100 ms`。等待 CPU
  在 failed CAS 后让出时，holder 会拿到完整 quantum；holder 释放后，waiter
  也要等 RR tick 才能恢复，因此短临界区可被放大成数百毫秒的 guest 等待。
- 候选：`0088` 只在真实跨核 failed S32C1I 后请求下一个 RR quantum 为
  `1 ms`。默认仍为 `100 ms`，环境变量
  `M5SW_XTENSA_CONTENDED_CAS_FAIR_YIELD=1` 才启用。
- 未修复：候选显著减少 CAS amplification，但没有改变 normal-WDT stage-1
  reset，也没有产生 startup UI。

## 证据

### 同 binary 5 秒 A/B

两轮使用相同 public firmware、QEMU binary 和 WDT-off 诊断控制；只有
`M5SW_XTENSA_CONTENDED_CAS_FAIR_YIELD` 不同。

| 指标 | control | candidate 1 ms |
| --- | ---: | ---: |
| S32C1I 操作 | `1,070,625` | `91,465` |
| 跨核 contended | `984,964` | `2,702` |
| CAS episodes | `212` | `16` |
| episode time | `2.239772672 s` | `1.017736288 s` |
| `xTaskQueueMutex` time | `1.861772640 s` | `1.017736288 s` |
| CPU0 freeze PC | `0x40087986` | `0x400951fe` |
| SSI `0x05` | `2,078` | `2,086` |
| SSI `0xBB/64` | `2,386` | `2,394` |

SSI 工作近似不变，说明差异不是 Flash 数据面速度，而是 spinlock 调度。
control 的 CPU0 位于 `0x40087980..8e` handoff-spin 簇，candidate 已移出。

### 20 秒与量子边界

20 秒 WDT-off control/candidate 的 CAS 为 `4,219,480/545,962`，
contended 为 `3,700,764/13,758`，episode time 为
`15.330116502/10.449083200 s`；两个 lane 的 SSI `0x05` 都是 `12,897`，
`0xBB/64` 都是 `11,845`。

`100 us` 对照把 5 秒 episode 数降到 `1`，但 CPU0 仍在
`0x40087986` handoff-spin 簇，10 秒仍在 `0x40087982`；因此保留 `1 ms`。

### normal WDT

| lane | stage-1 timeout | QEMU reset |
| --- | ---: | ---: |
| control | `17.249439933 s` | `17.249535709 s` |
| candidate | `17.248017950 s` | `17.248020126 s` |

两轮串口均为 `TG0WDT_SYS_RESET`，均未到 `BOARD NAME` 或 `APIKEY`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | 38-patch QEMU source snapshot incremental build |
| transport | PASS | 真实 Device Service `/api/v1`、QEMU、串口与 QOM |
| device_response | PASS | freeze state、CAS、SSI、TIMG/WDT counters |
| data_behavior | PARTIAL | contention 大幅下降，但 normal-WDT startup 仍 reset |
| visual_or_physical | NOT RUN | 无应用帧、物理硬件、RF、电气或 cache/PSRAM timing |

平台回归 `1560 tests OK, 10 skipped`；runtime coverage、peripheral catalog、
QEMU profiles、project snapshot 和 `0088` reverse-check 均 PASS。PR #40 的
两个检查 run 和 merge commit main run 通过。

## 验证边界

- WDT-off 是诊断 control，不是支持的修复。
- `1 ms` 只改变 host RR scheduling，不改变 guest atomic、lock owner 或
  watchdog deadline。
- `100 us` 减少 episode time，但没有改善 CPU0 handoff-spin 位置。
- MTTCG 与 deterministic `-icount` 不兼容；移除 `-icount` 的试验仍触发 WDT
  reset，且不属于可复现验收 lane。
- `RUNTIME-03` 继续 `OPEN`；不能把调度归因写成 legacy firmware PASS。

## 风险与回滚

补丁默认关闭；不设置环境变量时保持原 `100 ms` RR 行为。反向应用 `0088`
可恢复旧调度。所有测试 session 停止前保留 evidence，并以 `purge=0` 释放
lease；没有硬件烧录或不可逆操作。

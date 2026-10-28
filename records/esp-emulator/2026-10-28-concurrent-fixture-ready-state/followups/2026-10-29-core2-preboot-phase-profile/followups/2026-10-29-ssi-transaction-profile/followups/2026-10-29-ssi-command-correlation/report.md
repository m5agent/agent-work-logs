# ESP Emulator Core2 legacy SSI command correlation 报告

## 背景

`0071` 已确认 controller 边界约五万组 `0x05` 与约五万组 `0xBB/64`，
但没有 command-length 联合键或按 command 的 gap。本步目标是确认两者的
交替顺序和实际等待归属。

## 改动

`0072` 在 `0071` metrics 上增加：

- 4096 槽 command-length 稀疏表；
- 1024 槽 per-command gap 稀疏表；
- 1024 槽 command transition 稀疏表；
- 每张表的 overflow 计数；
- freeze trace 输出与 runner 总量校验。

所有表通过既有 metrics `memset` reset，只在 explicit pause/freeze 输出；
不改变 SPI 数据、guest 调度、WDT 或 accelerator。

## 联合分布

| Command / RX bytes | Count |
| --- | ---: |
| `0x05 / 1` | `50,071` |
| `0xBB / 64` | `49,882` |
| `0x00 / 0` | `1,561` |
| `0x00 / 1` | `3,567` |
| 其它 | `265` |
| 合计 | `105,346` |

`0xBB -> 0x05` 为 `49,582`，`0x05 -> 0xBB` 为 `49,600`，确认
`0xBB/64 -> 0x05/1 -> 0xBB/64` 主循环。

## Gap 归因

全部 gap：`105,345`、总时长 `79,699,282,877 ns`、最大
`2,687,751,164 ns`。

| 当前 command | Total gap | Share | Average |
| --- | ---: | ---: | ---: |
| `0x05` | `65,670,563,678 ns` | `82.398%` | `1.3115489 ms` |
| `0x00` | `13,849,241,407 ns` | `17.377%` | `2.698079 ms` |
| `0xBB` | `152,263,360 ns` | `0.191%` | `3.05 us` |
| 其它 | `28,533,432 ns` | `0.036%` | 约 `110 us` |

因此主要预算位于 64-byte read 后、下一次 status read 前。controller 收到
status command 后的单次数据动作不是主要耗时点。

## Normal WDT

- stage-0 timeout `7.249439872 s`；
- stage-1 timeout `17.249439902 s`；
- first reset `17.249440926 s`；
- TG1 feed `14,999`；
- TG1 max interval `3.926688 ms`；
- TG1 timeout `0`；
- classification `BOOTLOADER_TG0_STAGE1_RESET_WITH_TG1_LIVE`。

instrumentation 没有改变 `RUNTIME-03` 边界。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU 重建、patch reverse-check、1411 项平台回归 |
| transport | PASS | 完整 command-length/gap/transition 计数 |
| device_response | PASS | 两轮 WDT-off 主循环结构一致 |
| data_behavior | PARTIAL | 已定位到 `0x05` 前 gap，具体 guest driver/IRQ 未命名 |
| visual_or_physical | NOT RUN | 本轮不捕获应用帧；物理硬件未使用 |

## 验证边界

所有结果都是 virtual-device controller instrumentation，不证明物理 Flash、
cache、总线、RF、功耗或实时性能。WDT-off 是诊断控制，不是产品修复。

## 风险与回滚

`0072` 只增加 bounded aggregates 和 freeze 输出；回滚会使下一轮诊断退回
`0071` 的独立直方图，无法区分 status/read 交替和 per-command gap，但不会
删除 `.work` 原始证据或改变既有 guest 行为。

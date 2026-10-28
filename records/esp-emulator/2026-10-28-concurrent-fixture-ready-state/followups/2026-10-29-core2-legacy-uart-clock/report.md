# ESP Emulator Core2 legacy UART 与虚拟时钟对齐报告

## 背景

- 来源：Core2 legacy UIFlow `RUNTIME-03` 的 normal-WDT reset。
- 现象或需求：此前只有串口文件和 WDT/SSI trace，无法把 guest 输出精确
  对齐到虚拟时间。
- 目标：确认 reset 前是否已有 board/APIKEY/boot.py 进度，以及降低
  accelerator 是否能消除问题。

## 结论

- 状态：`PARTIAL`。诊断时间线成立，但没有关闭 startup UI 门禁。
- 根因边界：normal-WDT first reset 发生在 BOARD/APIKEY 之前；WDT-off
  下 guest 在同一阶段仍持续执行 SSI/cache handoff，不是永久 deadlock。
- 改动范围：UART TX trace 增加 virtual timestamp；runner 增加逐字节串口行
  重组和上限；资料、合同测试和 bootstrap ordering 同步更新。

## 证据

### 代码

- `0070-esp32-uart-tx-virtual-clock.patch` 仅改变 opt-in
  `M5SW_UART_TRACE` 的输出格式；
- `run_pause_sweep.py` 将 `[uart-tx] now=...` 重组为
  `start_ns/end_ns/text`；
- UART FIFO、tx callback、guest 指令和 WDT 语义未改变。

### 执行

| 行 | 虚拟时间 |
| --- | ---: |
| banner done | `2.7724 s` |
| BOARD NAME | `54.9955 s` |
| APIKEY | `55.0017 s` |
| boot.py start | `77.1092 s` |
| boot.py done | `77.6151 s` |

WDT-off 80 秒状态：CPU0 `0x4008798e`、CPU1 `0x40095b31`，SSI
`104,061` transactions，DPORT cache-sync `218,396`，cross-core writes
`432,918`。

normal WDT：

| shift | stage-0 | stage-1/reset |
| --- | ---: | ---: |
| `5` | `7.2529 s` | `17.2529 s` |
| `2` | `5.5609 s` | `15.5609 s` |

`shift=2` 运行到 reset 仍未出现 BOARD NAME，TG1 继续 feed 且 `0`
timeout。该 control 否定“只调 accelerator 即可修复”的假设。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU rebuild、patch reverse-check、C/source contracts |
| transport | PASS | 实际 UART TX bytes、SSI transactions、handoff trace |
| device_response | PARTIAL | WDT-off 到 BOARD/APIKEY/boot.py；normal WDT 未到 |
| data_behavior | PARTIAL | 双核/SSI/cache 进度真实，但 startup UI 未执行到 |
| visual_or_physical | NOT RUN | 该轮未捕获有效应用帧；物理硬件未使用 |

## 验证边界

WDT-off 只是诊断，不是产品修复。UART 时间来自 QEMU virtual clock，不是
物理串口时序。没有 matching source/ELF/MAP，不能命名全部 long-phase
guest 函数。未证明启动 UI、setup/REPL 或非空帧。

## 风险与回滚

`0070` 默认关闭、只增加诊断文本，不改变 UART 数据面；回滚只会移除
时间戳和 runner 串口行摘要，不影响已经收集的完整 raw trace。

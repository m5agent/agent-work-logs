# ESP Emulator Core2 flash-IPC diagnostic boundary

> Corrected by
> [the fixed flash/IPC follow-up](followups/2026-10-26-fixed-flash-ipc-wdt/README.md).
> The earlier spinlock owner mismatch came from a 4096-byte local buffer
> overflowing a 4096-byte CPU1 task stack. Do not reuse this page's spinlock
> diagnosis as runtime-model evidence; the corrected probe reaches partition
> reads and isolates an intermittent interrupt-WDT instead.

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户要求结合近期 Core2 工作重新整理代码与文档，并确认旧页面
  是否仍把未证实假设写成当前事实
- 源码版本：
  [m5stack-esp-emulator @ e185b15](https://github.com/m5agent/m5stack-esp-emulator/commit/e185b15b4a2d2bdbbe86f94e84de2217b40da55c)
- Base commit：`ad1d878d73af0d8b99e2a47809414f671c432bf3`
- 环境：macOS arm64；Python 3.13；ESP-IDF 5.5.4；Core2 QEMU
  virtual-device；物理硬件 `NOT RUN`

## 结论

新增一个不依赖 legacy UIFlow 的最小 ESP-IDF 5.5.4 探针，并在 3 个独立
Device Service lease 中稳定复现：CPU0/CPU1 PRID 分别为
`0xcdcd`/`0xabab`，CPU1 已打印 READY，但 CPU0 主任务在
`xQueueSemaphoreTake()` 退出临界区时触发 `spinlock_release()` owner
mismatch；三次均未到达 `esp_partition_read()` 的 `READ_START` marker。

因此当前证据不支持继续把“partition read/flash 数据面”写成已经确认的首个
失败点。当前最高优先级是采集实际 spinlock 地址、owner 和 `S32C1I`
compare-and-swap 的输入/结果。该结论是 `runtime_model_gap` 候选，不是已定位
根因，也不证明 QEMU 的 S32C1I 已实现错误。

文档已同步纠正 `RUNTIME-03` 的状态、Backlog、工作流、交接、代码地图、历史
调查和验证台账。`RUNTIME-03` 仍为 `OPEN`，legacy UIFlow 黑帧与
interrupt-WDT 仍未闭环，物理硬件未验证。

## 关键证据

- 主诊断 QEMU `a4045595…`：3/3 first boot 在 `READ_START` 前触发
  spinlock owner assertion；
- 旧 portable QEMU `4095fb11…` control：2/3 first boot 同类 assertion，
  1/3 first boot interrupt-WDT，三轮均无 `READ_START`；
- 固件 merged image `7e786a27…`；ELF `af6d765b…`；
- 符号化栈：
  `spinlock_release <- vPortExitCritical <- xQueueSemaphoreTake <-
  app_main <- main_task`；
- 全平台测试 `500/500 PASS`；文档领域契约 `40/40 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、Ruff `E9/F`、JSON 解析和 diff check 均 PASS。

## 文件

- `report.md`：问题、改动、证据、边界与回滚；
- `run.json`：机器可读结果；
- `evidence/core2-flash-ipc-summary.json`：脱敏的复现、符号化和验证摘要。

## 未覆盖项

- 没有取得错误 spinlock 地址、owner 值或单条 `S32C1I` 操作结果；
- 没有修复 QEMU 模型，也没有把最小探针推进到 `READ_START`；
- 没有重新验证 legacy UIFlow 非空应用帧；
- 没有证明最小失败与 legacy interrupt-WDT 的单一因果关系；
- 物理 multicore、flash-cache、PSRAM timing、RF、电气和真机均为
  `NOT RUN`。

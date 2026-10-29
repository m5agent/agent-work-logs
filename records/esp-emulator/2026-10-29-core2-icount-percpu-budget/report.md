# ESP Emulator Core2 per-vCPU icount fairness budget 报告

## 背景

- 来源：`RUNTIME-03` 和 PR
  [#45](https://github.com/m5agent/m5stack-esp-emulator/pull/45)。
- 现象：public legacy Core2 在 normal WDT 下于约 `17.24 s` reset，
  BOARD/APIKEY、setup/REPL 和非空应用帧均未完成。
- 目标：验证此前归因的跨核 IPC 固定延迟是否来自双 vCPU deterministic
  `-icount` 的 round-robin budget，并在保持真实 guest/WDT/Flash 数据面的
  前提下修正这一调度放大器。

## 结论

默认 `10 us` per-vCPU cap 在相同 firmware、trace 和 22 秒 control 下把
CPU1 initiator `can_start -> IPC return` 从 `563.667 us` 降到
`56.249 us`，peer Flash block wait 从 `728.443 us` 降到 `184.689 us`。
`100 us` 与 `1 us` 边界 control 都不如 `10 us`，说明继续压低预算会增加
宿主切换成本。

候选没有关闭 `RUNTIME-03`。90 秒 capped 长窗仍在 `17.242875841 s`
触发 TG0 stage-1 reset，说明剩余成本需要从 guest handoff 周期、启动
生命周期或其他 controller 路径继续解释。

## 改动范围

- QEMU `0090` 增加经校验的 `M5SW_ICOUNT_MAX_PERCPU_NS`；
- `qemu_accel.py` 为 Core2 默认导出 `10000`，并支持显式 `0`/A-B；
- `run_pc_trace.py --ipc-phases` 增加双向 initiator/peer phase 汇总；
- 新增平台契约测试、QEMU patch、状态页、Backlog、台账和 evidence。

guest 指令、normal WDT、Flash/SSI 数据面、中断语义和外设模型未修改。

## 执行

- QEMU：`568079f3…`
- firmware：`4d2d648b…`
- runtime：`qemu-wifi`
- icount：`shift=5,align=off,sleep=off`
- WDT：normal，未关闭或延长
- 短窗：22 秒 wall-time，uncapped 与 capped 各一轮
- 长窗：90 秒 wall-time，capped

被否定的 control：

- 全局 `memw` 让出：导致每轮 handoff 多秒延迟和 WDT panic 循环；
- cross-core write 强制 yield：可改变部分 phase，但总体不如 `10 us` cap；
- `100 us` 和 `1 us` budget：前者降幅不足，后者宿主切换成本回升。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU 冷构建、patch reverse-check |
| transport | PASS | Device Service 上传、QEMU serial/frame、BIN-bound trace |
| device_response | PARTIAL | Core2 UIFlow2 设备组 PASS；legacy normal-WDT 仍 reset |
| data_behavior | PARTIAL | IPC phase 改善；启动 UI/REPL 未完成 |
| visual_or_physical | NOT RUN | 黑帧；没有硬件或物理测量 |

平台测试 `1574 OK + 1 skip`。PR 的四个 CI check 全部 PASS。

## 验证边界

该 cap 只改变宿主单线程 TCG 的 vCPU 调度粒度，不证明墙钟、物理
cache/Flash timing、RF、电气或任意 legacy 固件兼容。PC 名称为
BIN-bound source shape，不是 matching linker symbol。

## 风险与回滚

风险是 fine-grained switch 增加宿主开销；因此保留 `0` 关闭开关。回滚可
移除 `0090` 和 Core2 默认值，`icount` 指令计数、WDT 和 peripheral path
不需迁移。没有持久设备或数据变更。

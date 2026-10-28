# ESP Emulator Core2 legacy SSI transaction profile 报告

## 背景

- 来源：`RUNTIME-03` pre-boot phase profile 已证明约十万次 SSI
  transaction，但抽样事件不足以给出完整 command/length 分布。
- 目标：增加 controller 级精确聚合，判断是否存在单个大块操作被拆成
  小 transaction，或 guest 本来就在执行大量独立命令。

## 改动

- `0071` 在现有 `Esp32HandoffMetrics` 增加 16-bit command 计数、
  RX-length `0..255`/`256+` bucket、gap bucket 和 gap 汇总；
- 每笔 transaction 开始时统计上一笔 end 到当前 start 的 virtual time；
- 仅在 explicit pause/freeze 时输出非零 histogram；
- reset 继续走既有 `memset(Esp32HandoffMetrics)`；
- 不修改 SSI 数据、调度器、WDT 或 accelerator 参数；
- runner 解析并验证三个 histogram 的计数一致性。

## 执行

### WDT-off 无 PC sampling

80 秒冻结点：

- transactions `104,302`；
- `0x05` `49,489`；
- `0xBB` `49,586`；
- command total `104,302`；
- RX-length total `104,302`；
- gap count `104,301`；
- gap total `79,699,109,375 ns`；
- gap max `2,693,165,726 ns`。

### WDT-off 有 PC sampling

同 SHA、同 runtime/profile、50 ms PC sampling：

- transactions `104,975`；
- `0x05` `49,908`；
- `0xBB` `49,736`；
- gap total `79,694,773,694 ns`；
- gap max `2,678,539,837 ns`。

两轮请求分布和 gap 形状相近，说明高 transaction count 不是 PC sampling
造成的 artifact。

### Normal WDT

- stage-0 timeout `7.253601472 s`；
- stage-1 timeout `17.253601473 s`；
- first reset `17.253695649 s`；
- TG1 feed `14,998`；
- TG1 max interval `3.926687 ms`；
- TG1 timeout `0`；
- classification `BOOTLOADER_TG0_STAGE1_RESET_WITH_TG1_LIVE`。

该结果与 instrumentation 前的 `17.2536 s` 边界基本重合。

## 结论

controller 边界确实收到约五万组独立 `0x05` 和约五万组
`0xBB/64-byte` command；没有观察到“一个更大 guest read 被 QEMU 拆成
这些小 transaction”的证据。已统计的相邻 command gap 总和覆盖 80 秒窗口
的约 `99.6%`，主要时间在 guest 两次 SPI command 之间，而不是单次不可见
的 controller bulk 操作。

这只缩小问题范围，不足以命名 guest driver 函数。`RUNTIME-03` 保持
`OPEN`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | QEMU 增量重建、patch reverse-check、1409 项平台回归 |
| transport | PASS | controller command/RX-length/gap 精确计数 |
| device_response | PASS | 两轮 WDT-off 同 SHA 结果稳定 |
| data_behavior | PARTIAL | command cadence 已定位；具体 guest driver/IRQ 未命名 |
| visual_or_physical | NOT RUN | 本轮不捕获应用帧；物理硬件未使用 |

## 验证边界

当前数据是 virtual-device controller instrumentation。FPGA/真机 Flash、
cache、总线、实时时钟、功耗和电气行为未验证。WDT-off 仅用于诊断，不是
产品修复；扩大 timeout、accelerator override 或 retry 都不能替代。

## 风险与回滚

`0071` 只增加默认关闭的 freezes 输出和内存计数，不改变 transaction
数据。回滚会移除 histogram/gap 字段，使下一轮诊断重新退化为采样分布；
不会删除已保留的 `.work` 原始证据。

# Core2 completed handoff trace and current-state consolidation

- 日期：`2026-10-26`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 源码版本：
  [m5stack-esp-emulator @ e420570](https://github.com/m5agent/m5stack-esp-emulator/commit/e420570ebdfe89dae75612938fbe80281c5413ef)
- Base commit：`5f68d70f51f39eef82113f6836843ef5b996ef23`
- 环境：macOS `26.5.1` arm64；Python `3.13.15`；QEMU 9.2.2 virtual Core2；
  physical hardware `NOT RUN`

## 结论

本轮补上了 `0038` exact-time freeze 之后的两个缺口：

1. `0039` 在暂停点直接读取两核 PC/IRQ、handoff flags、DPORT/cache、SSI 和
   cross-core counters；
2. `0040` 以默认关闭的 BIN-bound PC 列表统计 handoff setter。

结果否定了此前的“单次 cache handoff 永久不返回”和 UART storm 解释。首轮
normal-WDT run 在 `5.913935 s` 进入 stage-0 timeout、`15.914787 s` 首次
reset；reset 前 complete/can-start 的四个 setter 各命中约 `4,377` 次。
CPU1 在 CPU0 等待期间继续执行，SSI/cross-core 活动也继续增长。

同一 public legacy 固件仍然没有 REPL 或非空应用帧，因此
`RUNTIME-03` 继续为 `OPEN`。下一门禁改为首个 stage-0 timeout 后 WDT
feed/service 为何不能恢复，以及启动 workload 的累计 virtual time。

本轮还把当前事实、Backlog、工作流、代码地图、运行时缺口、历史调查、验证
台账和自动快照统一到上述结论，避免旧文档继续写成“某个 cache restore
未返回”。

## 关键证据

- `0039` patch SHA256：
  `eef62a556f5f213f3cbd25c5c3961f9ec71aeb2ea143cdcb1085f4f4152652cd`
- `0040` patch SHA256：
  `abc1c4c2cfb289f854ebd476c640db1dc4a36869b184faa20564a7e70f856d18`
- normalized public firmware SHA256：
  `152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc`
- QEMU binary SHA256：
  `f7ac5a0352eb4345f5c3b719a5dd656c5c0cdfb3d805cf258f144d1ae1fb6718`
- state-sweep evidence SHA256：
  `a52cd42709849e4ef25e5ad34f8dd534f437c277ae7cc3d87f061beb5cc0784c`
- setter-trace evidence SHA256：
  `6019d0ed2f084a27388105f972a852cf961cdf1dfe4303f33be3a974eed38b0c`
- platform tests：`515/515 PASS`
- Core2 targeted tests：`35/35 PASS`
- product CI：run `40240632355` 的 `platform-contracts` 与
  `network-namespace-policy` 均 `PASS`
- full UIFlow2 matrix after `0039/0040`：`NOT RUN`
- physical cache/PSRAM, RF, electrical and hardware validation：`NOT RUN`

## 文件

- `report.md`：实现、执行、结论、文档整理、边界和回滚；
- `run.json`：机器可读结果；
- `evidence/core2-handoff-state-sweep-summary.json`：三点 exact-time 状态和
  controller counters；
- `evidence/core2-handoff-pc-trace-summary.json`：setter 计数、period 和黑帧；
- `evidence/verification.summary.json`：测试、patch 校验和 CI 结果。

## 未覆盖项

- 没有取得 matching `UIFlow_Core2 v1.15.4` ELF/MAP；
- 没有证明首个 stage-0 timeout 后具体哪条 WDT feed/service liveness 路径失败；
- 同一固件仍只有 MicroPython banner、REPL 缺失、black frame 和 WDT reset；
- `0039/0040` 后没有重跑完整 UIFlow2 矩阵；
- 所有结果都是 `virtual-device validation`，不是物理 cache 时序、RF、功耗、
  电气或真机结论。

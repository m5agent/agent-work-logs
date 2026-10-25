# Core2 completed handoff trace report

## 背景

public `UIFlow_Core2 v1.15.4` 在 virtual Core2 中仍只到 MicroPython banner，
随后进入 watchdog reset 和黑帧。`0038` 已把调查收敛到最后一次 TG1 feed 后的
`800 ms` 窗口，但当时仍无法区分：

1. 某一次 cache restore/SSI/DPORT handoff 永久未返回；
2. 大量已经完成的同步周期累计超过 watchdog budget；
3. 首次 stage-0 timeout 后，另一条 WDT feed/service liveness 路径未恢复。

## 实现

### `0039` exact-time state dump

`0039-esp32-handoff-state-dump.patch` 扩展 `0038` 的 pause hook：

- 在指定 virtual time 暂停前输出两核 PC、PS、`INTSET`、`INTENABLE` 和
  interrupt request；
- 读取 `0x3ffc7ec8/c9`、`0x3ffc7750/54`；
- 输出 DPORT cache control、cache-sync 调用/页计数、SSI transaction/byte
  计数和 cross-core write 计数；
- 支持诊断专用 `M5SW_ESP32_HANDOFF_PAUSE_ACTION=exit`，每个隔离 lease 只取
  一个采样点，避免永久挂起 QEMU。

### `0040` BIN-bound setter trace

`0040-xtensa-handoff-pc-trace.patch` 新增默认关闭的 `M5SW_XTENSA_PC_TRACE`：

- 只接受显式 BIN-bound PC 列表，不进行高频全局 PC sampling；
- 每次命中输出 virtual time、CPU、PC、PRID、PS、INTENABLE 和 INTSET；
- 本轮跟踪 complete/can-start 的四个 set/clear setter：
  `0x40087965`、`0x4008797a`、`0x40087a25`、`0x40087b02`。

## 执行

固件：

```text
UIFlow_Core2 v1.15.4
normalized SHA256: 152127c808b9212e3a5b55dd9e0a2d24e71b902e225452b67db381c76caba1cc
```

Runtime：

```text
macOS 26.5.1 arm64
Python 3.13.15
QEMU 9.2.2 virtual Core2
QEMU binary SHA256: f7ac5a0352eb4345f5c3b719a5dd656c5c0cdfb3d805cf258f144d1ae1fb6718
```

### Three exact-time samples

| target | CPU0 PC | CPU1 PC | cache-sync calls | changed pages | SSI transactions | cross-core writes |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `14.8 s` | `0x40087980` | `0x40084487` | 16144 | 6679 | 6984 | 40274 |
| `15.3 s` | `0x40087980` | `0x40084487` | 16180 | 6679 | 6998 | 40566 |
| `15.9 s` | `0x40095733` | `0x4019622f` | 17444 | 6679 | 7506 | 43584 |

SSI RX bytes were `236116`、`236571`、`253081`。CPU0 在早期窗口等待时，
CPU1、SSI 和 cross-core 活动继续增长，因此两核整体永久停止被排除。

### Completed setter cycles

normal-WDT run：

| event | virtual time |
| --- | ---: |
| first stage-0 timeout | `5.913935 s` |
| first WDT reset | `15.914787 s` |

| setter | event | first-boot count |
| --- | --- | ---: |
| `0x40087965` | clear complete | 4377 |
| `0x4008797a` | set can-start | 4377 |
| `0x40087a25` | clear can-start | 4377 |
| `0x40087b02` | set complete | 4376 |

Serial 只有 banner、无 REPL；frame 仍是 302-byte PNG，SHA256
`57580743a08a3f4ebdf57240cbcc997002ef63b7234531f946127f1495973f43`。

## 结论

- “单次 complete/can-start handoff 永久不返回”不被证据支持；
- UART storm 解释继续废弃；
- CPU1 和 controller activity 在 CPU0 等待期间持续运行；
- legacy 启动仍在 stage-0 timeout 后失去 feed/service progress；
- 下一门禁是解释首个 stage-0 timeout 前后的 WDT feed、service task 和
  controller liveness，以及累计 virtual time 落在哪些 guest/controller 操作。

## 代码和文档整理

当前结论已同步到：

- 顶层 README；
- 项目当前状态与 Backlog；
- 运行时模型缺口登记；
- 工程交接、工作流、QEMU 适配矩阵和代码地图；
- 历史 Core2 cache/WDT 调查；
- 验证台账、测试说明、patch 索引和平台说明；
- 自动项目快照。

文档契约新增 `0039/0040` patch、runner、evidence 和当前事实断言；快照重新
生成后 `project_snapshot.py --check` 幂等通过。

## 验证

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | `compileall`、Ruff `E9/F`、Node SHA/upload 测试 |
| data_behavior | `PASS` | exact-time state sweep 和低扰动 setter trace 可重放 |
| artifact binding | `PASS` | firmware/QEMU/runner/evidence SHA 固定；`0039/0040` retained-tree reverse check |
| platform regression | `PASS` | 平台 `515/515`；Core2 定向 `35/35` |
| generated contracts | `PASS` | runtime coverage、peripheral catalog、QEMU profiles、project snapshot |
| delivery | `PASS` | product commit `e420570`；CI `40240632355` 两个 job 均 PASS |
| legacy application | `FAIL` | banner-only、无 REPL、black frame、WDT reset |
| full UIFlow2 matrix | `NOT RUN` | 本轮没有在 `0039/0040` 后重跑 67 cases |
| physical hardware | `NOT RUN` | 无真机、RF、电气或物理 cache/PSRAM 测量 |

## 验证边界

- 所有功能结果都是 `virtual-device validation`；
- BIN-bound PC 不等于 matching ELF symbol；
- 多次 handoff 完成不等于所有 cache/DPORT 操作都正确；
- watchdog reset 的 virtual timing 不是物理时间或功耗结论；
- 本记录不把模型缺口、legacy 固件失败和文档整理混成单一 PASS。

## 风险与回滚

没有烧录、擦除或持久设备状态修改。`0039` 只在显式设置 pause 环境变量时
启用；`0040` 默认关闭，只接受显式 PC 列表。回滚 product commit
`e420570ebdfe89dae75612938fbe80281c5413ef` 可恢复前一运行路径。retained
QEMU worktree 含既定板级修改，不能 reset/clean。

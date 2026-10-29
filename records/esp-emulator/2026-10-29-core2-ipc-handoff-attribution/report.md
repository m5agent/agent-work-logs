# ESP Emulator Core2 IPC/flash handoff stack attribution 报告

## 背景

- 来源：`RUNTIME-03`，PR
  [#41](https://github.com/m5agent/m5stack-esp-emulator/pull/41)。
- 现象：legacy UIFlow 在 pre-boot 阶段持续进行 Flash/cache handoff，
  normal WDT 在 BOARD/APIKEY 前触发 TG0 stage-1 reset。
- 目标：确认 `17.2 s` 时两核的实际执行路径，并排除由分频 trace 造成的
  虚假 Flash 事务时长解释。

## 结论

- 状态：`PARTIAL`（virtual-device validation）。
- CPU0：三次 exact-time freeze 都位于 `0x40087980..8e`，`A9` 指向
  `0x3ffc7ec8`。BIN 控制流与 public ESP-IDF
  `spi_flash_op_block_func` 的 `complete` busy-wait 顺序匹配。
- CPU0 调用栈：稳定包含 `0x400889c4`（`ipc_task` source shape）和
  `0x40087950`（block function），说明它是在跨核 Flash/cache handoff
  中被主动 park。
- CPU1：三次 PC 各不相同，并另一次捕获到
  `xQueueGenericSend` 的 `A0=0x801ec834`，返回 `esp_ipc_call_and_wait`
  source shape。CPU1 仍在推进 IPC 和启动工作。
- 永久 handshake deadlock：`REJECTED`。
- `RUNTIME-03`：仍 `OPEN`。

## 改动范围

`run_pause_sweep.py` 新增 `--trace-sample`，默认仍为 `1024`；每个 snapshot
记录有效 sample 值。没有修改 guest、QEMU controller、WDT deadline 或
peripheral path。文档新增 exact-time stack、source-shape 和 sampling 边界。

## 执行

环境：

- public `UIFlow_Core2 v1.15.4` normalized Flash；
- `runtime=qemu-wifi`；
- `icount shift=5`；
- normal WDT；
- QEMU SHA256
  `75e7fa97424c859c6e1fe918dda203aa2c6509e9c81937893a15d2a4a46b6714`。

三次独立 lease 均在 `17.200000 s` 附近 freeze，误差 `29-31 ns`，并启用
64-word stack 和 24-word object dump。三次 serial 完全相同：

- 507 bytes；
- SHA256
  `e996276519b4f8882739ff1c494dcecba313c99278857a53a984c1c9986a1b62`；
- 没有 `BOARD NAME`、`APIKEY` 或 setup/REPL。

## 结果

| run | CPU0 PC | CPU1 PC |
| --- | --- | --- |
| 1 | `0x40087988` | `0x40084312` |
| 2 | `0x40087984` | `0x4008448a` |
| 3 | `0x4008798e` | `0x40095c5c` |

另一次同条件 freeze 的 CPU1 位于 `0x40094e92` 的
`xQueueGenericSend`，`A0=0x801ec834`。这提供了 cross-core IPC 的直接
BIN-bound 路径，同时三次最终样本的变化否定固定双核停止。

2 秒 `--trace-sample 1` 控制记录：

- 13 个 `transaction-begin`；
- 13 个 `transaction-end`；
- 11 个 `receive-data`；
- 13 对 begin/end 全部为同步 `0 ns`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | Python runner contract 与完整平台回归 |
| transport | PASS | 真实 Device Service `/api/v1`、QEMU 和串口状态 |
| device_response | PASS | exact-time register/stack/object/serial freeze |
| data_behavior | PARTIAL | handoff 路径已归因，normal-WDT 启动仍失败 |
| visual_or_physical | NOT RUN | 没有 startup UI、应用帧或物理硬件证据 |

平台回归为 `1560 tests OK, 10 skipped`；runtime coverage、peripheral
catalog、QEMU profiles、project snapshot 和 `git diff --check` 均 PASS。
PR #41 的两个检查 run 均 PASS，并已 merge 到
`3e424ee83567a7813f4d8862b24323a4cd500152`。

## 验证边界

- 没有 matching private legacy ELF/MAP；函数名只由同一 BIN 的指令形状和
  public IDF source 对照得到。
- `0.4 秒单事务` 来自把 1024 分频后的不同事件错误配对，已由 full-trace
  control 拒绝。
- exact-time stack 证明当前热点和状态，不证明某个永久死锁。
- normal WDT、startup UI、setup/REPL、非空应用帧、物理 cache/PSRAM timing
  和真机仍未通过。

## 风险与回滚

runner 改动只增加显式 trace 分频控制，默认行为保持 `1024`。反向应用 merge
commit 可恢复旧 runner。所有运行使用临时 Device Service lease 和 QEMU
`-snapshot`；没有硬件烧录、不可逆操作或凭据变更。

# m5stack-linux-dtoverlays PR #20 第二轮：ff4cd84 复核（recheck / READY / .shutdown restart）

- 日期：`2026-11-27`
- 结果：`PARTIAL`（四项修复在主机级 harness 上全部通过；实机与虚拟设备未跑）
- 工作类型：`pr_review`
- 条目：[m5stack/m5stack-linux-dtoverlays#20](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20)
  「powerfail_suo: orderly poweroff from the power slider」，作者 shrimpapplepro，英文，OPEN
- 新评论：<https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7200264330>
  （2026-11-26T18:16:36Z，作者称四项全部处理于 `ff4cd84`，并要求补跑两个场景）
- 已发布回复：<https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7200515708>
- 源码：head `ff4cd84474787ea24a00b65d83b5b50e4a51c1c9`，
  base `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`；自 base 起 2 文件 `+333/-73`，
  本提交 `+161/-97`
- 环境：macOS arm64；无 Cardputer Zero 实机；Device Service `cardputer-zero`
  profile `supported=false creatable=false backend_ready=false`
  （`__missing_qemu__` / `__missing_rom__`）；无内核头文件，docker 守护进程仍因
  `/var/lib/desktop-containerd/...` 只读而无法起容器
- 证据等级：**host-level test**（驱动源码不改，stub 内核头 + 模拟 M5IOE1 状态机与模拟时间）
  \+ code-level verification（overlay 重编与语义 diff、内核 API 核对、参考寄存器表核对）

## 结论

四项改动都与评论描述一致，两个被点名的场景按预期工作，没有阻塞问题。

- `DEBOUNCE(2)` 不再被当成"仍开机"：500 ms 的 `check` 读到 2 会每 100 ms 重查，
  只在 `0xB6` 为 3/4 或读失败时才进入 orderly；线路为低期间 IRQ 保持关闭，
  线路回高后才重新使能（T6）。
- 关机倒计时期间线路回高：不进入 orderly、不挂 backstop、立即重新使能 IRQ；
  `READY(0xB0)` 在 `0xB6` 回到 1 之后写一次 1（T7）。
- `.shutdown` 时若 `slider_off` 且线路为高：走 `emergency_restart()`，不再写 200 ms、
  不拉低 disabled-gpios；线路为低仍按 200 ms 切电（T8/T9）。
- 最小保持 12000 ms 使 backstop 不早于翻转后 8 s；clamp、`m5stack,power-hold-ms`
  前缀、移除 `disabled-gpios` 回退都已落实（T3/T12/T13/T14）。

两个非阻塞残留：

1. **restart 只存在于 `.shutdown`。** 如果关机过程本身卡住（正是 backstop 存在的场景），
   `.shutdown` 永远不会执行：backstop 只做 SysRq S+U，倒计时结束后 M5IOE1 拉低 PWR_EN，
   但拨杆（SW_EN 二极管或）继续供电，板子停在半关机状态、文件系统已只读、LED 走马灯。
   T25 复现了这条序列（`restart_calls == 0`，S+U，芯片回到 state 1）。
   在 backstop 里补一次线路采样并 `emergency_restart()` 只能覆盖 hold-4 s 之前的回高；
   T26 显示 backstop 采样之后（例如 18 s）再回高仍然没有 restart 点。完整收口需要在
   `powerfail_orderly()` 之后持续轮询线路直到切电（例如 500 ms 一次）。本记录附的 proposal patch
   只做前者：harness 下 T25 通过、T26 不变、其余 24 个场景不变（108 checks）。
2. **irq-gpios 读失败没有出口。** `gpiod_get_raw_value_cansleep()` 返回错误时新代码每 100 ms
   无限重查：不进入 orderly、不挂 backstop、IRQ 保持关闭、OFF_TIME 仍是 20000（T19）。
   这正是本次修复针对的"长时间可写 + 硬切"窗口，只是需要 GPIO get 失败才触发
   （SoC GPIO 上基本不会发生）。有界重试后再走 orderly（或还原 2000 + legacy）即可。

另外，第一轮无法确认的寄存器语义这次有独立来源：作者引用的
[prokrypt/CardputerZero-Open-IOE1](https://github.com/prokrypt/CardputerZero-Open-IOE1/blob/4369350e13ba29087b98f39169e57d31e9629e33/README.md)
在 `4369350` 的 README 与 `firmware/main.c` 中写明：`0xB6` 0-4、state 3 实时重读 OFF_TIME、
倒计时清 `READY(0xB0)` 且可由 host 写 1、OFF_TIME 最小 200 且按单次写（两字节一起）、
state 2 最多 100 ms，以及 boost 由 SW_EN 与 PB7 二极管或供电（拨杆开时 Pi 不受 PY32 影响）。
这与作者的寄存器表和实机结论一致；注意它是声明与 stock 对齐的第三方重实现，不是 stock 二进制。

## 关键证据

- `code/build.sh`：两个二进制（head；带 proposal 的 `powerfail_suo_proposed.c`）。
  head 26 个场景 / 109 checks 全过，proposal 108 checks 全过；见
  `evidence/host-harness-head.txt`、`evidence/host-harness-proposed.txt`
- 点名的两个场景：`evidence/requested-scenarios.txt`（T7 / T8 / T25）
- 参考寄存器表与状态机：`evidence/reference-register-map.txt`
- overlay：`dtc 1.8.1` 重编 head 无 warning，dtbo sha256 `33309ef4...`；
  base→head 反编译 diff 恰好是两条属性 + 一个 local fixup；
  `5623292→ff4cd84` 恰好是属性改名；`evidence/overlay-compile.txt`
- 内核：`emergency_restart()` 为 `EXPORT_SYMBOL_GPL`，可在非 IRQ 上下文调用，
  会先把 `system_state` 置为 `SYSTEM_RESTART`；`evidence/kernel-api-checks.txt`
- 本机 profile：`evidence/local-profile-summary.txt`
- 可选 patch：`git apply --check patches/0001-proposal-backstop-restart.patch` 在 ff4cd84 上通过
- 条目元数据与范围：`evidence/pr-metadata.txt`

## 逐项复核（对应作者评论）

| 作者声明 | 复核结果 | 证据 |
| --- | --- | --- |
| check 是 delayed_work，500 ms debounce 即其 delay | 成立，翻转后 500 ms 运行 | T5/T6 |
| 线路低且 `0xB6` 为 1/2 时每 100 ms 重查 | 成立；T6 中 1500/1600/1700 均读到 2，1800 读到 3 才决策 | `evidence/requested-scenarios.txt` T6 |
| 只有线路回高才重新使能 IRQ，不丢关机 | 成立；低电平期间 `enable_irq` 计数为 0，回高后 1 次 | T6/T7/T24 |
| 只有 3/4 或读失败进入 orderly | 成立；state 2/1 只重查，state 读错走 orderly | T6/T20/T22 |
| 倒计时期间回高：不关机，READY 恢复 | 成立；T7 无 orderly/backstop，`0xB0<-1` 只在 state 1 后写一次 | T7 |
| `.shutdown` 回高：`emergency_restart()` 而非停机 | 成立；且不写 200 ms、不拉低 disabled-gpios | T8 |
| 最小保持 12000，backstop 不早于 8 s | 成立；从最后一次非倒计时观察起算 | T12 |
| backstop 从最后一次"未倒计时"观察起算，宁早不晚 | 成立；T6 的 cut 估计比真实切电早 50 ms，backstop 早 4.05 s | T6 |
| `m5stack,power-hold-ms` 前缀 | 成立；无前缀属性被忽略 | T14 |
| 移除 `disabled-gpios` 回退 | 成立；只有 disabled-gpios 指向 M5IOE1 时仍是 legacy | T3 |
| 实机 retest（boot、4.1 s、4.9 s restart、W=1） | 未独立复跑 | NOT RUN |

## 提议的 backstop 收口（未推送）

`patches/0001-proposal-backstop-restart.patch`：在 backstop 的 S+U 之后，若
`slider_off` 且线路为高，则 `emergency_restart()`。理由：此时文件系统已只读，
拨杆已经要求"开机"，而 M5IOE1 因 SW_EN 无法真正断电。harness 在应用该 patch 后
T25 从"无 restart"变为"重启"，T26（backstop 之后的回高）仍无 restart，其余 24 个场景全部不变。
该 patch 只是部分收口，未发到上游。

## 未覆盖项

- hardware validation：`NOT RUN`。无 Cardputer Zero；作者的 4.1/4.9 s 关机、
  15.7 s 兜底、下次启动 fsck 干净均为自述。
- virtual-device validation：`NOT RUN`。`cardputer-zero` profile 不可创建，
  缺 QEMU/ROM，后端为 Linux ARM64。
- 内核模块 `W=1` 重编：`NOT RUN`。无内核头文件；docker 守护进程不可用。
- 计时真实性：`NOT RUN`。1 jiffy = 1 ms；未建模 I2C 传输耗时、workqueue 并发、
  `cancel_delayed_work_sync()` 与正在运行的 work 的竞争。M5IOE1 模型按 50 ms 轮询量化。
- `<stock dtbo> 字节一致`：仓库内 `firmware/CardputerZero/overlays/cardputerzero-overlay.dtbo`
  （sha256 `e4425fee...`）反编译后没有 powerfail 节点，是更早的构建，
  因此无法用仓库内容复核"a3fd3e8 的 v5 overlay 与实机 stock dtbo 字节一致"；
  只复核了 base→head 的源码级差异。
- 参考寄存器表来自第三方重实现（声明 stock 对齐），不是 stock 二进制逆向结果的独立复算。

## 风险与回滚

只读评审：未关闭 PR、未 push 上游、未改他人仓库。记录中的 patch 仅作为建议，
不应用于上游；若作者采纳，按正常 PR 流程走。回滚即忽略该记录。

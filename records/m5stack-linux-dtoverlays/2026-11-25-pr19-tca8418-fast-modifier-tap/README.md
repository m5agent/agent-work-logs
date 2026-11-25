# m5stack/m5stack-linux-dtoverlays #19：Sym/Aa/Fn 轻点后快速按键不再遗留层

- 日期：`2026-11-25`
- 结果：`PARTIAL`（上报场景在主机级状态机测试中通过；残留一个同类窄窗口；真机与内核构建未跑）
- 工作类型：`pr_review`
- 条目：[m5stack/m5stack-linux-dtoverlays#19](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/19)
  「tca8418: fast key after a Sym/Aa/Fn tap no longer leaves the layer on」，
  作者 prokrypt，英文，OPEN，无历史评论，无 review
- 源码：PR head `e7f7a18650977fa99971f1e82d741ba5058e7fdc`，base `main`
  `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4`；2 文件，`+54/-7`，单 commit
- 环境：macOS arm64；本机无 Cardputer Zero 硬件；本地 Device Service 的
  `cardputer-zero` profile 不可创建（`backend_ready=false`，
  `__missing_qemu__` / `__missing_rom__`）；无 Linux ARM64 内核头文件，无法重建模块
- 证据等级：**host-level test** + code-level verification（userspace 状态机，
  与本机 Device Service 的 `cardputer-zero` 情况见下）
- 已发布回复：见 `run.json` 的 `source.comment`（1 条，英文；PR 仍 OPEN，
  未 close、未 push 上游、未改他人代码）

## 结论

补丁对它声称的两种场景是正确的，无阻塞问题；另有一个**同一症状类的窄残留窗口**，
该窗口在改动前就存在，不是本 PR 引入的。

1. 上报场景（轻点修饰键后 300 ms 内按键并松开）在 `main` 上确实停在
   `ST_ONESHOT` 且 `layer_active=1`，下一个键继续出符号；PR head 上变为
   `ST_IDLE` / `layer_active=0`。复现与修复都在主机级 harness 中独立得到。
2. 快速和弦（修饰键按下、普通键、修饰键先松开）同样由 bug 变为 `IDLE`；
   “修饰键先松、普通键后松”的顺序也正确。
3. 未回归：普通轻点—停顿—单键 one-shot、长按 hold、双击锁定/退出锁定、
   “修饰键按下前已按住的键”滚动场景，输出与 `main` 完全一致。
4. 残留：`ST_WAIT_ACTIVE_LEAVE` 只在 `EV_OTHER_KEY_RELE && used` 时消费层，
   `EV_TIMEOUT_300` 分支（`tca8418_fsm.c:139`）不看 `used`。若那个键在 300 ms
   边界仍被按住（或还有别的普通键按着，导致 `tca8418_dispatch_other_key_release()`
   因“全部松开”门控而没被调用），层会重新进入 `ST_ONESHOT`，下一个键仍是符号。
   序列 `KEY_PRES, KEY_RELE, OTHER_KEY_PRES, [300 ms], OTHER_KEY_PRES` 在 PR head
   上得到 `ONESHOT, layer=1`，在 `main` 上同样是 `ONESHOT`。给该分支加
   `if (me->used) consume_layer(me);` 后变为 `IDLE, layer=0`，其余序列不变
   （见 `patches/0002`）。

## 关键证据

- `evidence/host-harness.txt`：10 条基线序列（pre-fix / PR head）与 2 条残留
  序列（PR head / 加保护后）的完整状态、`layer_active`、`used` 输出。
- `evidence/host-harness-pr-head.txt`、`evidence/host-harness-pre-fix.txt`：
  两版基线输出的分文件版本。
- `code/`：可重建的 harness（`build.sh`），包含 `fsm_pre_fix.c`、
  `fsm_pr_head.c`、三种 harness 与 stub 头文件；PR head 与加保护版本的差异
  见 `patches/0002`。
- `evidence/pr-metadata.txt`：PR 状态、作者、scope、base/head、评论与检查。
- `evidence/local-profile-summary.txt`：`cardputer-zero` profile 为
  `supported=false`、`creatable=false`、`backend_ready=false`，缺 QEMU / ROM。
- `patches/0001-tca8418-fast-modifier-tap.patch`：PR 原始提交（base `a3fd3e8`）。

## 未覆盖项

- hardware validation：`NOT RUN`。本机无 Cardputer Zero 硬件；作者自述在
  arm64 6.18 上实测，未独立复跑。
- virtual-device validation：`NOT RUN`。`cardputer-zero` profile 不可创建，
  缺 QEMU/ROM，其后端是 Linux ARM64，不是 ESP32 固件目标。
- 内核模块构建（`W=1`，arm64 6.18）：`NOT RUN`。本机无内核头文件/交叉工具链。
- 计时与 IRQ 批处理：`NOT RUN`。harness 按有序事件驱动，未模拟真实 300 ms
  定时器抖动、中断批量顺序或 `cancel_delayed_work_sync` 的并发时序。
- LED / input 事件序列：`NOT RUN`。stub 只统计 `emit_*` / `led_*` 调用次数，
  没有验证真实 LED 状态与 input 子系统的上报顺序。

## 文件

- `report.md`：完整评审、状态机推演、验证矩阵与边界
- `run.json`：机器可读记录
- `code/`：可重建的主机级 harness 与两版 FSM 源码
- `evidence/`：harness 输出、PR 与本地 profile 摘要
- `patches/`：PR 原始提交、建议的 timeout 保护 diff

# 评审报告：tca8418 快速按键消费层（PR #19）

## 1. 条目与范围

| 项 | 值 |
| --- | --- |
| PR | m5stack/m5stack-linux-dtoverlays#19 |
| 标题 | tca8418: fast key after a Sym/Aa/Fn tap no longer leaves the layer on |
| 作者 | prokrypt |
| 状态 | OPEN，MERGEABLE，无历史评论与 review |
| base | `main` `a3fd3e83c0247e16e194e7e40f7fc1f5be933dd4` |
| head | `e7f7a18650977fa99971f1e82d741ba5058e7fdc`（单 commit） |
| 规模 | 2 文件，+54/−7：`modules/tca8418-1.0/tca8418_fsm.c`、`tca8418_keypad_m5stack.c` |

改动内容：

1. 新增事件 `EV_OTHER_KEY_PRES` 与每实例标志 `used`。
2. 普通键按下时向三个修饰键 FSM 各发一次 `EV_OTHER_KEY_PRES`；`ST_ACTIVE`
   与 `ST_WAIT_ACTIVE_LEAVE` 据此置 `used=1`（`ST_ACTIVE` 入口清零）。
3. `ST_ACTIVE` 收到自身 `EV_KEY_RELE` 且 `used` 已置位时走新的
   `consume_layer()`，直接回 `ST_IDLE`，而不是进入 300 ms 判定窗口。
4. `tca8418_dispatch_other_key_release()` 现在也向 `ST_WAIT_ACTIVE_LEAVE`
   的实例分发 `EV_OTHER_KEY_RELE`，`used` 置位则消费层；仅当状态真正变化时
   才更新 300 ms 定时器。
5. 状态机整体结构（`IDLE / ACTIVE / WAIT / ONESHOT / HOLD / LOCKED*`）不变。

## 2. 问题与根因

Cardputer Zero 上轻点 Sym / Aa / Fn 后 300 ms 内按键，符号会输入，但层不会关闭：
超时仍把状态推进到 `ST_ONESHOT`，下一个键继续出符号。

根因在 `main` 的 `tca8418_fsm.c`：轻点后状态为 `ST_WAIT_ACTIVE_LEAVE`，此时层已
启用；窗口内普通键按下不产生任何 FSM 事件，键松开时
`tca8418_dispatch_other_key_release()` 只向 `ST_ONESHOT` 的实例分发
`EV_OTHER_KEY_RELE`，`ST_WAIT_ACTIVE_LEAVE` 被跳过，随后 300 ms 超时进入
`ST_ONESHOT`，层继续对下一个键生效。快速和弦（修饰键按住时按普通键）同理：
`ST_ACTIVE` 不处理 `EV_OTHER_KEY_RELE`，修饰键松开后仍进入 `ST_WAIT_ACTIVE_LEAVE`
→ `ST_ONESHOT`。

## 3. 验证方式

证据等级：**host-level test**（userspace 状态机 harness）+ code-level verification。
没有使用 virtual-device validation：本地 Device Service 的 `cardputer-zero`
profile 是 Linux ARM64 后端且不可创建（`backend_ready=false`、
`missing_runtime_files=["__missing_qemu__","__missing_rom__"]`），没有可运行的
Linux 目标；ESP32 系列 profile 与本驱动所跑的 SoC 不同，不能替代。

harness 做法与提交者描述一致：把 `tca8418_fsm.c` 直接 include 进一个 userspace
翻译单元，stub 掉 `<linux/*.h>` 与 `emit_key_pres_status()` /
`emit_key_release_status()` / `led_*()`，用事件序列驱动 `tca8418_dispatch()`，每一步
打印 `state / layer_active / used`。被测的两版源码分别是 `main` 的
`tca8418_fsm.c` 与 PR head 的同名文件（`code/fsm_pre_fix.c`、
`code/fsm_pr_head.c`）。事件顺序按驱动真实行为编排：`EV_OTHER_KEY_RELE` 只在
“全部普通键松开”时发送（`tca8418_keypad_m5stack.c:521`）。

重建命令（`code/build.sh`）：

```sh
tmp=$(mktemp -d); mkdir -p "$tmp/stub/linux"
cp stub/linux/*.h "$tmp/stub/linux/"
cp harness.c "$tmp/"; cp fsm_pr_head.c "$tmp/tca8418_fsm.c"
gcc -Wall -Wextra -std=gnu99 -I "$tmp/stub" -I "$tmp" -o /tmp/h_pr "$tmp/harness.c"
/tmp/h_pr
```

`build.sh` 对四个变体重复该过程，`-Wall -Wextra` 下无 warning。

## 4. 结果

### 4.1 基线 10 条序列

| # | 序列 | `main` 结果 | PR head 结果 | 判定 |
| --- | --- | --- | --- | --- |
| 1 | 轻点 + 300 ms 内按键并松开（上报 bug） | `ONESHOT`, layer=1 | `IDLE`, layer=0 | 修复 |
| 2 | 和弦（键先松） | `ONESHOT`, layer=1 | `IDLE`, layer=0 | 修复 |
| 3 | 和弦（修饰键先松） | `ONESHOT`, layer=1 | `IDLE`, layer=0 | 修复 |
| 4 | 轻点—停顿—单键（one-shot 正常路径） | `IDLE`, layer=0 | `IDLE`, layer=0 | 不变 |
| 5 | 轻点后一直等（one-shot 待命） | `ONESHOT`, layer=1 | `ONESHOT`, layer=1 | 不变 |
| 6 | 长按 hold | `IDLE`, layer=0 | `IDLE`, layer=0 | 不变 |
| 7 | 双击锁定 + 退出 | `IDLE`, layer=0 | `IDLE`, layer=0 | 不变 |
| 8 | 轻点 + 键按住跨过 300 ms + 下一键 | `ONESHOT`, layer=1 | `ONESHOT`, layer=1 | 残留（见 4.2） |
| 9 | 修饰键按下前已有键按住（roll） | `ONESHOT`, layer=1 | `ONESHOT`, layer=1 | 不变 |
| 10 | 锁定状态下普通键松开 | 保持 `LOCKED_WAIT_LEAVE` | 保持 `LOCKED_WAIT_LEAVE` | 不变 |

`main` 上 1、2、3 三条命中 bug，与提交者的描述一致；PR head 上全部按预期。

### 4.2 残留窗口（同一症状类，改动前已存在）

`ST_WAIT_ACTIVE_LEAVE` 只新增了 `EV_OTHER_KEY_RELE && used` 的消费路径，
`EV_TIMEOUT_300` 分支仍然无条件进入 `ST_ONESHOT`（`tca8418_fsm.c:139`）。因此：

- 轻点后按下的那个键若在 300 ms 边界仍被按住，超时先把状态推到 `ONESHOT`
  （层仍启用），此时再按第二个键仍会被映射成符号；
- 或者轻点时另一个普通键仍按着，`tca8418_dispatch_other_key_release()` 因
  “全部松开”门控尚未被调用，`used` 已置位但不会被消费，超时同样进入 `ONESHOT`。

实测序列 `KEY_PRES, KEY_RELE, OTHER_KEY_PRES, TIMEOUT_300, OTHER_KEY_PRES`
在 PR head 上得到 `ONESHOT / layer=1`；`main` 上同样得到 `ONESHOT`，所以不是本 PR
引入的回归。给该分支加 `if (me->used) consume_layer(me);`（`patches/0002`）后
两条残留序列都变为 `IDLE / layer=0`，而 10 条基线序列的输出与 PR head 完全相同
（`evidence/host-harness.txt` 末段）。

## 5. 影响面与风险

- 结构改动小，仅新增事件、一个 per-instance 标志和一个消费路径；`IDLE` /
  `ONESHOT` / `HOLD` / `LOCKED*` 语义未动。
- `used` 只在 `ST_ACTIVE` 入口清零，而对象由 `devm_kzalloc()` 分配
  （`tca8418_keypad_m5stack.c:767`），初始为 0；每个新 ACTIVE 周期都会重置，
  不存在跨周期的脏值影响。
- `tca8418_dispatch_other_key_release()` 中的新 `tca8418_fsm_update_timer()`
  只在该实例状态变化时调用。新增的取消路径针对的是一枚尚未到期的 300 ms
  delayed work；`keypad_data->wq` 是 `alloc_ordered_workqueue()`
  （`tca8418_keypad_m5stack.c:777`），超时 work 不可能与 IRQ work 并发执行，
  未发现等待自身的路径。该结论为代码级推演，未做真实中断压力测试。
- 行为变化：和弦结束后立即再轻点修饰键不再被当成双击锁定的第二击（因为已经
  回到 `IDLE`）。这与“和弦已经消费了层”的语义一致，未发现实际使用上的回归。
- 回滚：还原该 commit 即可，无持久化状态、无 ABI/DT 变化。

## 6. 未覆盖项

- hardware validation：`NOT RUN`，本机无 Cardputer Zero。
- virtual-device validation：`NOT RUN`，`cardputer-zero` profile 不可创建且缺
  QEMU/ROM；ESP32 profile 不是同一执行路径。
- 内核模块构建（arm64 6.18，`W=1`）：`NOT RUN`，本机无内核头文件/交叉工具链；
  提交者自述构建通过，未独立复核。
- 真实计时与 IRQ 批处理顺序、`cancel_delayed_work_sync` 与定时器到期的竞争：
  `NOT RUN`，harness 以有序事件驱动。
- 真实 LED 状态与 input 事件上报顺序：`NOT RUN`，stub 只统计调用次数。
- CI：仓库只有 WeCom 摘要转发工作流，没有内核模块构建作业。

## 7. 结论

补丁对上报的“轻点后快速按键”和“快速和弦”两类场景正确，未发现阻塞问题，
可以合并。残留的 `WAIT + used + TIMEOUT` 窄窗口与上报症状同类、在 `main` 上
已经存在，建议作者判断是否顺手用 `patches/0002` 的一条分支一起收掉；即使
不并入，也不影响本 PR 的修复价值。

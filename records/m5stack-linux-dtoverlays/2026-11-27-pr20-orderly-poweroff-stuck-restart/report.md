# PR #20 第三轮复核：3b6d273 的卡住关机 restart 与 irq-gpios 读失败上界

## 对象

- PR：`m5stack/m5stack-linux-dtoverlays` #20「powerfail_suo: orderly poweroff from the power slider」
- 作者：`shrimpapplepro`
- 上一轮回复：comment 7200515708（针对 `ff4cd84`，提出两个非阻塞残留）
- 本轮作者评论：comment 7200881588（2026-11-26T18:48:53Z），称两项在 `3b6d273` 完成
- 本轮源码：`3b6d2738d8606581cddf3f34e213e7682ad9d23d`（相对上一轮只改 `modules/CardputerZero/powerfail_suo.c`，+43/−9）
- 基线与 PR 状态：`a3fd3e8`，OPEN，`MERGEABLE`，无 CI check

## 结论

两项修复在 host-level harness 上均成立，未发现阻塞问题：

1. **卡住的关机 + 拨杆回开**：backstop 先做 SysRq S + U，等 1.5 s（`POWERFAIL_REMOUNT_WAIT_MS`），
   之后每 200 ms（`POWERFAIL_STUCK_POLL_MS`）读一次 `irq-gpios`；高电平即
   `emergency_restart()`，否则继续排程，直到 M5IOE1 在保持窗口末尾断电。S + U 只做一次，
   `.shutdown` 的 `cancel_delayed_work_sync()` 能停掉整个自排程链。
   - 回开发生在 backstop 之前（T25，t=8000）：17000 S+U → 19500 首次轮询即重启，`restart_calls == 1`。
   - 回开发生在 S+U 之后（T26，t=19000）：下一次轮询 19500 重启，S + U 仍只有一次。
   - 回开落在两次轮询之间（T27，t=19600）：19700 重启。
   - 不回合：轮询按 200 ms 继续到断电，不误重启，也不重复 S + U（T28）。
   - 关机在轮询开始后完成（T29）：`.shutdown` 取消 backstop，写 200 ms、拉低 LCD 复位，
     之后不再有排程，无重启。

2. **irq-gpios 读失败**：`gpio_errors` 逐次累加，第 10 次失败后仍在 100 ms 重查，
   第 11 次（`++gpio_errors <= 10` 不成立，约 +1.0 s）把 `val` 置 0，改由 `0xB6` 判定。
   - `0xB6` = 3（或不可读）→ orderly（T19：t=2500 进入 orderly，OFF_TIME 20000，backstop 17000；
     T31：GPIO 与 `0xB6` 同时不可读，同样在 2500 进入 orderly）。
   - `0xB6` = 2 → 继续等，不贸然关机（T30，debounce 拉长到 100 s）。
   - 恢复读取后计数清零并走正常路径（T32，两次失败后 t=1800 进入 orderly，`gpio_errors == 0`）。

同时确认上一轮的结论没有回退：legacy（无 `m5stack,power-controller`）仍只做 SysRq U；
`disabled-gpios` 回退仍不存在；`m5stack,power-hold-ms` 仍是带前缀属性、clamp 12–60 s；
`.shutdown` 在重启路径不改 OFF_TIME。

## 证据等级

- **host-level test + code-level verification**：驱动源码 `3b6d273` 原样编译（stub 内核头），
  时间与 delayed work 由 harness 模拟；32 个场景 / 127 checks 全过。
- 本机无 Cardputer Zero（`/api/v1/devices` 中 `cardputer-zero`：`supported=false`、`creatable=false`、
  `backend_ready=false`、缺 `__missing_qemu__` / `__missing_rom__`），**virtual-device validation NOT RUN**。
- 作者的实机日志、4.1 s / 4.9 s / 15.7 s 时序、ext4 与 fsck 结果**未独立复跑**（hardware validation NOT RUN）。

## 未覆盖项

- 实机行为与作者新给的「卡住关机 + 回开」时序未独立复跑；`W=1` 未跑（本机无内核头文件）。
- 计时为模型：未建模 I2C 事务耗时、workqueue 并发、`emergency_restart()` 实际复位时长。
- 作者日志中 02:45:54.758（S+U 的 remount）到 02:46:14.091（下一次 `Booting Linux`）相隔约 19 s，
  而按新代码 S+U 后 1.5 s + 200 ms 就应重启；单凭粘贴无法判断是重启后 journal 时间基准、
  复位耗时，还是日志拼接。已请作者补 `journalctl -b -1 -o short-monotonic` 的尾部。
- `.shutdown` 采样到断电之间的固有窗口（≤200 ms）：若拨杆恰在此间回开，SW_EN 维持升压、
  SoC 已 halt，无法由软件补救；属任何 halt-time 竞争，不作为修改请求。

# PR #20 第四轮复核：19 s 间隔的时间基准归因

## 背景与现象

上一轮（`3b6d273`）的复核结论是两项残留问题在代码中已关闭，但作者实机日志里有一个无法对齐的读数：

```
02:45:54.758  kernel: sysrq: Emergency Remount R/O        # 由 backstop 的 S+U 触发
02:46:14.091  kernel: Booting Linux on physical CPU 0x... # 下一次启动
```

按新逻辑，backstop 在 S + U 后等 1.5 s 再以 200 ms 轮询 `irq-gpios`，拨杆已回开时应在这 1.7 s 内调用
`emergency_restart()`。19.3 s 的间隔与 1.7 s 的预期不符，我请作者补
`journalctl -b -1 -o short-monotonic` 的尾部输出。

作者本轮回复（comment `7205879787`）给出的解释是：journald 约在本次启动 10.5 s 才开始，
它读入早期内核消息时按读取时刻打时间戳，`-o short-monotonic` 也因此把 `Booting Linux` 显示在 ~10.4 s；
用 RTC 与 `dmesg` 换算，内核实际在 02:46:03 左右启动，remount 后 8.5–9.5 s，其中包含驱动的
1.5 s + ≤200 ms 与 Pi 固件引导。

## 假设与验证

假设：`/dev/kmsg` 条目的 journal 时间戳取 journald 处理时刻，而非内核记录里的时间；若成立，
则 19 s 是读数偏差，不需要代码改动。

验证一（源码，code-level）：systemd v257 `src/journal/journald-server.c` 的
`server_dispatch_message_real()` 在写条目之前显式注释并调用 `event_dual_timestamp_now()`：

```
/* Get the closest, linearized time we have for this log event from the event loop. (Note that we do
 * not use the source time, and not even the time the event was originally seen, but instead simply
 * the time we started processing it, as we want strictly linear ordering in what we write out.) */
struct dual_timestamp ts;
event_dual_timestamp_now(s->event, &ts);
```

同一策略在 v252（Debian bookworm 代）也存在（`journald-server.c:820-836`），说明不是新版本行为。
内核自己的时间在 `dev_kmsg_record()` 里只写入 `_SOURCE_BOOTTIME_TIMESTAMP` 与
（为兼容保留的）`_SOURCE_MONOTONIC_TIMESTAMP`，不参与条目时间。因此 journald 启动瞬间批量读入的
早期内核行，`short-monotonic` 全部落在启动时刻，作者观察到的 ~10.4 s 与机制一致。

验证二（算术，code-level）：用作者给的两个锚点换算绝对时间：

| 量 | 值 |
| --- | --- |
| 上一次启动 base = 02:45:54.758 − 1919.200085 s | 02:13:55.558 |
| 本次内核启动 = 02:46:07 − 3.813891 s | 02:46:03.186–04.185（RTC 整秒） |
| remount → 内核启动 | 8.43–9.43 s |
| 驱动占用（1.5 s + ≤0.2 s） | ≤1.70 s |
| 余下（复位 + 固件引导） | 6.73–7.73 s |
| journal 行 02:46:14.091 − 内核启动 | +9.91–10.90 s（≈ journald 启动延迟） |

也就是说 19.333 s 的“间隔”由 ~8.4–9.4 s 的真实重启/引导加 ~10–11 s 的 journald 时间基准差组成，
与新代码的 1.5 s + 200 ms 不矛盾。作者“8.5–9.5 s”的表述与本记录“8.43–9.43 s”的差异只是 RTC 整秒取整。

验证三（状态检查）：PR head 仍是 `3b6d273`，本轮没有新提交；`mergeable=MERGEABLE`。因此本轮不需要
再跑代码矩阵，上一轮的 32 场景 / 127 checks 结论继续有效。本机 Device Service 的 `cardputer-zero`
仍是 `supported=false`、`backend_ready=false`（`linux-arm64` 独立后端，缺 QEMU/ROM），无法做
virtual-device 复跑。

## 结论

- 作者的归因成立：19 s 是 journal 时间基准问题，不是慢重启；源码策略与算术都支持这一点。
- 代码侧无需改动；上一轮唯一存疑点关闭，本轮无新残留。
- 实机时序、复位/固件阶段的拆分、板端 systemd 版本仍未独立验证。

## 未覆盖项与风险

- hardware validation `NOT RUN`：无 Cardputer Zero；未独立复跑 4.1 / 4.9 s、15.7 s backstop、fsck 结果。
- virtual-device validation `NOT RUN`：`cardputer-zero` 走独立 Linux 后端，`backend_ready=false`。
- 未读取板端 `systemd --version`；只核对了 v252 与 v257 源码，行为在两代之间一致。
- 8.43–9.43 s 中的 6.73–7.73 s 是复位还是固件引导，现有日志无法再拆分；这不影响“非慢重启”的结论。
- 作者日志里的 RTC 是整秒值，绝对时间有 ±1 s 不确定度。

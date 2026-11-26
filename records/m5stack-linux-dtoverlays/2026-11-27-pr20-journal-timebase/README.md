# m5stack/m5stack-linux-dtoverlays #20 第四轮：19 s 间隔归因于 journald 时间基准

- 日期：`2026-11-27`
- 结果：`PARTIAL`（作者解释在 code-level 与算术上成立；实机时序未独立复跑）
- 工作类型：`pr_review`
- 问题来源：[PR #20 作者新评论](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7205879787)（2026-11-26T23:48:34Z）
- 源码版本：`m5stack/m5stack-linux-dtoverlays` @ `3b6d2738d8606581cddf3f34e213e7682ad9d23d`（与上一轮相同，无新提交）
- 环境：macOS arm64；无 Cardputer Zero；Device Service `cardputer-zero` 不可运行（`supported=false`、`backend_ready=false`）
- 已发布回复：[PR #20 comment 7205940522](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7205940522)（1 条英文；PR 保持 OPEN，未 push 上游）

## 结论

上一轮唯一存疑点（S + U 到下一次 `Booting Linux` 相隔 ~19 s）**不是慢重启，而是 journal 的时间基准**
造成的读数偏差。作者的归因正确：

- `journald` 处理 `/dev/kmsg` 记录时，**不使用内核的原始时间**作为条目时间，而是用自己开始处理该条目的时刻
  （`systemd` `server_dispatch_message_real()` 注释原文：*we do not use the source time … but instead simply
  the time we started processing it*）。内核自己的时间只保存在 `_SOURCE_MONOTONIC_TIMESTAMP` /
  `_SOURCE_BOOTTIME_TIMESTAMP` 字段里（`dev_kmsg_record()`）。因此 journald 启动后一次性读入的早期内核行，
  其 `short-monotonic` 都落在 journald 启动时刻（~10.4 s），而不是 0 s。
- 用作者给的锚点做算术：上一次启动 base = 02:45:54.758 − 1919.200085 s = **02:13:55.558**；
  本次内核启动 = 02:46:07 − 3.813891 s = **02:46:03.186–04.185**（RTC 整秒粒度）。
  remount → 内核启动 **8.43–9.43 s**，其中驱动只占 1.5 s 等待 + ≤0.2 s 轮询，余下 **6.73–7.73 s**
  是复位后的固件引导阶段。
- journal 里的 `02:46:14.091` 相对内核启动是 **+9.91–10.90 s**，正对应作者说的 journald 启动延迟；
  19.333 s 的“间隔”里约 10–11 s 是 journald 时间基准差。

因此代码侧无需改动，上一轮的 19 s 疑点关闭；本轮没有新的残留问题。

## 关键证据

- journald 时间戳路径（源码摘录，v252/v257 两代一致）：`evidence/journald-timestamp-path.txt`
- 时间基准算术：`evidence/timestamp-arithmetic.txt`
- PR 状态、提交与评论时间线：`evidence/pr-metadata.txt`
- 本机 `cardputer-zero` profile（不可运行原因）：`evidence/device-service-cardputerzero.txt`
- 作者日志原文：见 PR comment `7205879787`（`dmesg` RTC 行、`-b -1 -o short-monotonic` 行）

## 文件

- `report.md`：归因过程、源码依据、算术与边界
- `run.json`：结构化记录
- `evidence/`：源码摘录、算术输出、PR 元数据、设备 profile

## 未覆盖项

- hardware validation `NOT RUN`：无 Cardputer Zero，作者实机时序未独立复跑
- virtual-device validation `NOT RUN`：`cardputer-zero` 走独立 Linux 后端，`backend_ready=false`，无 QEMU/ROM
- 板端 systemd 版本 `NOT RUN`：未读取实机 `systemd --version`；只核对了 v252 与 v257 两代源码行为一致
- 复位/固件阶段耗时 `NOT RUN`：8.4–9.4 s 中 6.7–7.7 s 无法从现有日志进一步拆分（复位本身 vs 固件引导）
- RTC 整秒粒度带来 ±1 s 不确定度；作者“8.5–9.5 s”与本记录“8.43–9.43 s”的差异来自取整

## 2026-11-27 回复

- 唯一一条英文回复：<https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7205940522>
- 结论：19 s 是 journald 时间基准差，不是慢重启；无需改代码，上一轮唯一存疑点关闭。
- 公开记录 permalink：<https://github.com/m5agent/agent-work-logs/blob/c050d7913f92c2763c042d4642b74123f3da9d81/records/m5stack-linux-dtoverlays/2026-11-27-pr20-journal-timebase/README.md>

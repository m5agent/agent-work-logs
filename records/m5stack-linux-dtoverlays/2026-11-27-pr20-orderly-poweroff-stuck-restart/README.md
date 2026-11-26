# m5stack/m5stack-linux-dtoverlays #20 第三轮：3b6d273 的卡住关机 restart 与 irq-gpios 读失败上界

- 日期：`2026-11-27`
- 结果：`PARTIAL`（两项修复在 host-level harness 上通过；实机与虚拟设备未跑）
- 工作类型：`pr_review`
- 问题来源：[PR #20 作者新评论](https://github.com/m5stack/m5stack-linux-dtoverlays/pull/20#issuecomment-7200881588)（2026-11-26T18:48:53Z）
- 已发布回复：（见下方「发布」）
- 源码版本：`m5stack/m5stack-linux-dtoverlays` @ `3b6d2738d8606581cddf3f34e213e7682ad9d23d`
- 环境：macOS arm64；无 Cardputer Zero；Device Service `cardputer-zero` 不可创建；无内核头文件

## 结论

上一轮两个非阻塞残留都已关闭，未发现新的阻塞问题：

- backstop 不再在 S + U 后结束：等 1.5 s 让 remount 落地，再每 200 ms 读 `irq-gpios`，
  高电平即 `emergency_restart()`，否则自排程继续（`powerfail_suo.c:124-156`）。
  回开在 backstop 之前 / S+U 之后 / 两次轮询之间三种位置都能重启（T25–T27）；
  不回合时不误重启、S + U 不重复（T28）；`.shutdown` 的 `cancel_delayed_work_sync()` 能停掉整条链（T29）。
- `irq-gpios` 读失败有上界：第 10 次仍失败后继续 100 ms 重查，第 11 次（约 +1.0 s）改由 `0xB6` 判定，
  `3`/`4` 或不可读 → orderly，`1`/`2` → 继续等；恢复读取后计数清零（`powerfail_suo.c:255-270`，T19/T30–T32）。

## 关键证据

- 构建/运行：`code/build.sh`；head 32 个场景 / 127 checks 全过
- 点名场景：`evidence/stuck-and-gpio-scenarios.txt`（T25–T32）
- 原始日志：`evidence/host-harness-head.txt`
- 本轮改动：`evidence/diff-ff4cd84-3b6d273.diff`（只改 `powerfail_suo.c`，+43/−9）
- 条目：`evidence/pr-metadata.txt`；本机 profile：`evidence/local-profile-summary.txt`

## 文件

- `report.md`：复核结论、逐场景结果、未覆盖项
- `run.json`：结构化记录
- `evidence/`：harness 原始输出、点名场景、diff、元数据、profile
- `code/`：可重建 harness、`3b6d273` 驱动源码、stub 头

## 未覆盖项

- hardware validation `NOT RUN`：无 Cardputer Zero；作者实机时序未独立复跑
- virtual-device validation `NOT RUN`：profile `backend_ready=false`，缺 QEMU/ROM
- 内核 `W=1` `NOT RUN`：无内核头文件
- 计时真实性 `NOT RUN`：未建模 I2C 耗时、workqueue 并发与复位时长
- 作者日志中 S+U 到下一次启动相隔约 19 s，与新代码 1.5 s + 200 ms 的预期不符，已请求
  `journalctl -b -1 -o short-monotonic` 尾部以排除日志拼接或时间基准问题

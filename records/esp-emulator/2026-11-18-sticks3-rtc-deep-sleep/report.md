# StickS3 RTC 定时深睡修复验证

## 背景与范围

既有运行时支持特定 RTC 浅睡路径。StickS3 上的标准 ESP-IDF 探针启用定时唤醒，并通过 `esp_deep_sleep_start()` 进入深睡。旧版在进入后仍报告 QMP `running`，没有出现 `SUSPEND` 或 `WAKEUP`，CPU 停在 panic 路径。修订支持定时深睡与数字域复位，保留 RTC 计时、唤醒原因和 RTC RAM。显式 API 复位另清理 RTC 暂存状态并恢复上电复位原因。[运行结果](evidence/rtc-deep-sleep.summary.json)

## 固定身份

| 项目 | 身份 |
| --- | --- |
| 执行服务源码 | `13df3b8a7ab197df14f57d2ca8bc58919a7eb666` |
| Device Service API | `1.89.0`，OpenAPI `2fbea7a0ec6d386dd6b6fa718d68291a3497eb7d3232feb85211ca93efa43cc1` |
| QEMU 基线及发布快照 | `40edccac415693c5130f91c01d84176ae6008566`、`66f91582a0dc15ccfb2502c5cad69d73b441a4bf` |
| 运行时补丁 SHA-256 | `6cbbc3fa9788e7692558a7aa43cf64b78e50f1a9801d52b0e6b52cf4f6ade974` |
| ESP-IDF v5.5.4 | `735507283d5b2f9fb363a1901172dbd9e847945d` |
| 原版探针合并镜像 | 8 MiB，`db7bfcc809651b3fad6a051bd5ebc3575007a3d2becdcdf028e883a6911c1f39` |
| 旧版原生运行时 | `90cb5df45fceef9bd63e9979986e4608c4e5264c8a95e453c167e8b0f0a2a68a` |
| 最终原生运行时 | `d18e5fa7aaebda01bd4cb6eac5d4da6c11a012025882f37d567554fc807a5f06` |

最终源码为 [`80a3b5eda5f50c4a8cced04e31021fc8363593ab`](https://github.com/m5agent/m5stack-esp-emulator/tree/80a3b5eda5f50c4a8cced04e31021fc8363593ab)。本地测试 2,440 项，2,430 通过、10 跳过。四项工件验证器、176 层标准补丁链验证及目标补丁反向校验均通过。[该提交的 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44254482005) · [主分支 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44254994638)

## 执行

1. 用固定 ESP-IDF 版本构建 `tests/firmware/sticks3_rtc_deep_sleep`，再运行 `idf.py merge-bin --fill-flash-size 8MB`。确认镜像和 ROM 哈希，使用隔离服务的 `sticks3`、`runtime=qemu` 和原生离线路由。
2. 逐轮核对 `SUSPEND → RESET → WAKEUP`、QMP 恢复 `running`、`RTC_DEEP_BOOT reset=8 cause=4` 以及 `RTC_DEEP_PASS cycles=2`。来宾核对数字域普通内存重新初始化，并校验 RTC 保留数据、慢钟计时及时间范围。
3. 调用正常的 `/api/v1/sessions/{id}/reset`，同一会话再次报告 `reset=1 cause=0`，RTC 起始时间为 26,050 µs，并完成相同两轮。停止前请求同一会话 ZIP，校验清单、固件及各文件哈希，清除活动租约并释放可写 Flash。
4. 独立启动同一最终运行时上的 All day watch 0.3.8 原版，使用语义 A、B 与 B 长按路径进入浅睡，随后用 B 键唤醒。保留 QMP 状态、唤醒画面和停止前 ZIP。[运行结果](evidence/rtc-deep-sleep.summary.json)

## 结果

| 项目 | 状态 | 观察 |
| --- | --- | --- |
| 旧运行时 | FAIL | 首次 650 ms 深睡请求后无 QMP suspend/wake，CPU 停在 panic。 |
| 中间候选一 | PARTIAL | 来宾通过，但一次证据与停止 API 返回 500。回收了所拥有的来宾。两轮隔离复测成功，首次错误原因未确认。 |
| 中间候选二 | PARTIAL | 定时唤醒通过，完整 RTC 复位失败。计数器重置与 SDK 校准基线不一致。 |
| 最终定时深睡 | PASS | 显式复位前来宾测得 807,282 和 1,655,839 µs；复位后测得 798,442 和 1,648,429 µs。两轮均通过来宾约束。 |
| 原版 Watch 浅睡 | PASS | 观察 65.095 秒，B 键后 QMP 从 `suspended` 回到 `running`，得到新唤醒帧，软件复位为零。 |

从精确提交重跑后，深睡探针仍在同一进程完成四次定时唤醒。独立混合 GPIO 与定时浅睡探针在挂起中执行普通 HTTP 复位，同一会话完成两个确认启动、两次首次定时返回，记录 `RESET → RESUME → SUSPEND → WAKEUP`。该轮未发出手工 QMP 控制命令。[深睡复验](evidence/exact-committed-deep.summary.json) · [浅睡复位复验](evidence/shallow-suspended-http-reset.summary.json)

这里的时间来自来宾 RTC 测量。实体硬件、耗电、浏览器、其他深睡唤醒源和电源域组合均未执行。未提交 Burner。[运行结果](evidence/rtc-deep-sleep.summary.json)

# StickS3 原生 RTC 定时深睡与原版浅睡回归

- 日期 `2026-11-18`
- 结果 `PASS`，范围为 StickS3 的定时深睡与原版浅睡回归
- 工作类型 `code_change`
- 工作来源 [StickS3 定时浅睡后续](https://github.com/m5agent/agent-work-logs/blob/74a37ab4c356d6656b60bf13d146a9bd1feca31b/records/esp-emulator/2026-11-17-s3-iwdt-observability/followups/2026-11-18-sticks3-rtc-gpio-light-sleep/followups/2026-11-18-sticks3-rtc-light-sleep-timer/README.md)
- 执行服务源码 [版本 `13df3b8a`](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666)
- 环境为独立 Device Service 1.89.0、`m5sticks3` 原生离线 QEMU、ESP-IDF v5.5.4

## 结论

同一 SDK 探针在最终原生运行时先完成 650 ms 和 1,500 ms 两轮深睡，显式 API 复位后在同一进程与会话内再次完成两轮。来宾报告定时唤醒与深睡复位，RTC 数据和计时保留，普通数字域内存重新初始化。独立运行的原版 All day watch 0.3.8 可由 B 键从浅睡唤醒。[验证摘要](evidence/rtc-deep-sleep.summary.json)

## 关键证据

- 旧运行时在同一探针的首次深睡请求后停在 panic 路径。保留失败及两个中间候选结果。
- 最终 Xtensa 运行时 SHA-256 为 `d18e5fa7aaebda01bd4cb6eac5d4da6c11a012025882f37d567554fc807a5f06`。同会话串口、QMP 和 ZIP 清单通过核验，停止后活动租约归零。
- 原版 Watch 浅睡回归观察 65.095 秒，保留同会话唤醒帧哈希与证据 ZIP。[验证摘要](evidence/rtc-deep-sleep.summary.json)

## 最终源码验证

公开 main 回读为 [`80a3b5eda5f50c4a8cced04e31021fc8363593ab`](https://github.com/m5agent/m5stack-esp-emulator/tree/80a3b5eda5f50c4a8cced04e31021fc8363593ab)。[精确源码深睡复验](evidence/exact-committed-deep.summary.json)和[浅睡挂起时正常 HTTP 复位回归](evidence/shallow-suspended-http-reset.summary.json)均通过。该提交的 `platform-contracts` 与 `network-namespace-policy` 均通过。[GitHub Actions](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44254482005)

## 文件

- [复现与验证报告](report.md)
- [结构化记录](run.json)
- [证据说明](evidence/README.md)
- [有界摘要](evidence/rtc-deep-sleep.summary.json)

## 未覆盖项

实体硬件和功耗、browser-WASM、EXT0/EXT1、ULP、触摸深睡唤醒、其他 RTC 慢钟和电源域组合均为 `NOT RUN`。未提交 Burner。

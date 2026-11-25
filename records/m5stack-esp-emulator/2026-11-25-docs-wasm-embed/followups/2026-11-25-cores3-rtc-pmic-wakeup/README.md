# CoreS3 Wakeup 的 RTC 和 PMIC 唤醒

- 日期 2026-11-25
- 工作类型 fix，virtual-device validation
- 结果 PASS，CoreS3 原始 Wakeup 固件在同一 Chrome 会话两次定时唤醒
- 设备 CoreS3，Chrome 158.0.8127.37，Apple Silicon macOS
- 问题来源 [模拟器 #252](https://github.com/m5agent/m5stack-esp-emulator/issues/252)
- 源码基线 `744df778ef78c03e783f51f4620bae89f3b3c9f3`，候选 `1e86d673400dc74b4be37da5d8d6ba71aaf44a5f`
- 原生运行时、真机、正式托管及日历闹钟 NOT RUN

相同固件此前在触摸后退出。修复后每轮都经过真实 RTC 定时、PMIC 唤醒、ROM 启动和来宾画面重绘。两次观察到休眠约五秒，随后来宾继续启动。正常退出时六个 Worker 均回收。启动途中旧提示画面可能短暂出现，第二次触摸等待完整重绘。

- [根因、重建与复验](report.md)
- [结构化执行记录](run.json)
- [锁定构建双轮唤醒](evidence/wake-two-cycle.summary.json)
- [无定时器普通关机对照](evidence/power-off-control.summary.json)
- [原始失败版本、I²C 写入](evidence/wake-baseline.summary.json)
- [首次候选过早触摸 PARTIAL](evidence/early-touch.summary.json)

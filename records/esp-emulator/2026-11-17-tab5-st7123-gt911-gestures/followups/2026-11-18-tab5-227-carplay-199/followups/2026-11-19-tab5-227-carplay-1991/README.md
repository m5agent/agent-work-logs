# Tab5 CarPlay 原版板型探测与触摸复验

- 日期 `2026-11-19`。
- 结果 `PASS`，覆盖 CarPlay 1.0.0 原版的 GT911 板型启动、界面和触摸。
- 类型 `issue`。 [原始问题 #227](https://github.com/m5agent/m5stack-esp-emulator/issues/227)
- 环境为隔离的 macOS arm64 Device Service 1.99.1、Espressif esp-emu 1.1.0 和 GT911／ILI9881C 模型。 [执行源码](https://github.com/m5agent/m5stack-esp-emulator/tree/c9ec0f274579b78d87a4a301147f351e8b7a48fa)

同一原版在 2.328 秒显示 720×1280 主页。GT911 的两次点击各有 13 份报告获来宾确认。空白点击保持主页，点击清除配对按钮打开应用自己的确认框。22.419 秒内只有一次 ROM 启动，没有旧板型断言或软件复位。

同会话 ZIP 的 CRC、清单和成员数据均通过回读。停机后历史可读，Flash 已释放，活动租约为零。P4、C6 和试验服务均已退出。

- [执行报告](report.md)
- [结构化运行摘要](run.json)
- [脱敏证据摘要](evidence/carplay-227-1991.summary.json)

USB DWC 枚举、iPhone 连接、其他板型、浏览器和实体硬件未执行。未确认清除配对，未提交 Burner。

# Tab5 CarPlay 原版板型探测和触摸复验

- 日期：`2026-11-18`
- 结果：`PASS`，限原版 CarPlay 的虚拟设备启动与 GT911 触摸。
- 工作类型：`issue`
- 问题来源：[m5stack-esp-emulator #227](https://github.com/m5agent/m5stack-esp-emulator/issues/227)
- 源码版本：[main 218106fa](https://github.com/m5agent/m5stack-esp-emulator/tree/218106fac28258325bed4a58091cf1217f67252f)，执行源码为与之仅相差文档的 `a729e24b1e4724b783ab2d59eec689cfdfeb24b3`。
- 环境：macOS arm64 的独立 Device Service 1.99.0，esp-emu 1.1.0，GT911／ILI9881C，P4 与 C6 伴生进程。

同一份 CarPlay 1.0.0 原版通过普通 Device Service 入口启动。1.538 秒读到
720×1280 原版主页。两次 GT911 点击各产生 13 份报告，来宾全部确认。
空白区域点击保持主页，点击清除配对按钮打开原版确认弹窗。
观察 22.634 秒内只有一次 ROM 启动，没有软件复位或旧板型探测断言。

停止后会话可读，可写 Flash 已释放，活动租约为零。P4、C6 和独立服务均已退出。
同会话证据 ZIP 通过 CRC 和清单逐文件校验。

- [执行报告](report.md)
- [运行说明](run.json)
- [脱敏证据摘要](evidence/carplay-227-199.summary.json)

未执行实机、其他板型的 CarPlay、浏览器、iPhone USB 握手、外部网络或独立的
GT911 复位引脚取证。未确认清除配对，未提交 Burner。

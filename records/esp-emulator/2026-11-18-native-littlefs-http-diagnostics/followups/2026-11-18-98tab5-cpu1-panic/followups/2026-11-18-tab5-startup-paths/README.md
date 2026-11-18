# Tab5 三份原版启动路径复验

- 日期为 2026-11-18。工作类型为原版固件启动诊断。
- 结果为 PARTIAL。三份原版启动路径已有具体观察，整机自然启动和交互仍待验收。
- 本轮跟进 [98TAB5 原版 CPU1 异常](../../README.md)及 [Tab5 原版取帧对照](https://github.com/m5agent/m5stack-esp-emulator/blob/80a3b5eda5f50c4a8cced04e31021fc8363593ab/docs/evidence/2026-11-18-tab5-stock-frame-comparison/README.md)。
- 环境为隔离 Device Service 1.89.0、原生 esp-emu 1.1.0 和 Tab5 P4/C6，验证类型为 virtual-device validation。固件、源码、ROM、eFuse 数据和运行时 SHA 均见回执。

98TAB5 自然启动 64 秒出现 33 次软件复位，未出完整帧。独立诊断轮在调试器正常分离后取到 20 张稳定的无启动盘画面。M5TabOS 在原版 75 秒自然观察中无复位，仍无完整帧。官方 UserDemo 的 CPU0 持续等待 CPU1 暂停状态位。

[完整报告](report.md) · [执行清单](run.json) · [98TAB5 启动窗口](evidence/98tab5-cache-window-summary.json) · [M5TabOS 与 UserDemo 回执](evidence/tab5-startup-paths-summary.json)

装载启动盘、真实触控、实体硬件和浏览器均未测试。未提交 Burner。

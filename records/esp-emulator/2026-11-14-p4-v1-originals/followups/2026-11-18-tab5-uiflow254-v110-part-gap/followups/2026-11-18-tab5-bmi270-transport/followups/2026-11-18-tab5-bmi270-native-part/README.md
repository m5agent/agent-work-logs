# Tab5 原版 UIFlow2 的 BMI270 初始化与原生触摸复验

- 日期为 `2026-11-18`，时区为 Asia/Shanghai。
- 整体结果为 `PARTIAL`，工作类型为 `issue`。
- 环境为隔离 Device Service `1.89.0` 与 esp-emu `1.1.0` 原生 ESP32-P4/ESP32-C6。
- 实现与执行版本为 `f7f6b53eed43257b21d9bec291088c8c5e2648f6`，证据版本为 `13df3b8a7ab197df14f57d2ca8bc58919a7eb666`。[问题 #188](https://github.com/m5agent/m5stack-esp-emulator/issues/188)

同一份原版 UIFlow2 v2.5.4 在 ST7123 和 GT911 上都完成了 BMI270 初始化。ST7123 渲染离线启动页，一次触摸打开 I²C Scan 页面。GT911 原版仍收到 DSI 零读回，未识别面板。ST7123 的 Arduventure 和 GT911 的 CarPlay 各通过一项原版触摸回归。

本轮覆盖 BMI270 标准配置的传输与初始化状态、离线启动及指定触摸动作。未执行扫描按钮、联网、配对、浏览器或实机验证。Burner 未提交。

- [执行报告](report.md)记录对照、积累的证据和复现设置。
- [运行清单](run.json)记录实现版本、环境、检查和文件哈希。
- [有界证据](evidence/README.md)链接四项 Part 回归和最终源码重放收据。
- [前次隔离诊断](../../README.md)保留旧传输缓冲区、BMI270 诊断 Part 与两种面板的现象。

## 后续复验

[原版 GT911 档案的 DSI 命令、回包和未识别分支](followups/2026-11-18-tab5-gt911-dsi-panel-read/README.md)

# PocketJS Tab5 触控与 PCM Applet 验证

- 日期为 2026-11-20，工作类型为报告，总体结果为 `PARTIAL`。
- 目标为将自定义 Applet 构建成 `.pocket`，并验证 Pocket Shell 启动、GT911 触控、画面变化与数字音频输出。
- 使用 Pocket M5 v0.1.4 锁定的 PocketJS `806ac202`，以及 Device Service 1.99.5、esp-emu 1.1.0 和 Tab5 GT911／ILI9881C 虚拟设备。

Applet 的打包、启动和交互功能通过。一次来宾会话中，6 次操作共获得 35 次 GT911 报告确认，屏幕跟随手势变换，串口和 I²S1 记录了 8 个音符。Applet 就绪前发生两次 P4 TLSF 断言复位。证据层级为 `virtual-device validation`。

- [执行方法与验证边界](report.md)
- [结构化结果](run.json)
- [同一会话的脱敏证据](evidence/virtual-device.summary.json)

真机、浏览器 WASM、外置 Unit、联网安装及实际扬声器听感未执行验证。无源仓库补丁。

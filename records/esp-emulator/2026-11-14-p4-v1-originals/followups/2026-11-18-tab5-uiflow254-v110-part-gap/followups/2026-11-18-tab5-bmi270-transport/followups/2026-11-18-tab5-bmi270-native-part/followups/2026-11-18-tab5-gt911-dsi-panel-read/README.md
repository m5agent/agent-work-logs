# Tab5 原版 UIFlow2 v2.5.4 的面板读取回包

- 日期：2026-11-18（UTC+08:00）。
- 范围：Tab5 [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188)，同一原版 BIN，GT911/ILI9881C 档案，Device Service 1.92.0、esp-emu 1.1.0。
- 验证：**virtual-device validation**。GT911 档案冷启动画面在有界观察中为 **FAIL**，#188 保持开放。
- 两次独立冷启动均记录了一次 DSI 零回包和一次原版 M5GFX 面板未识别，有效帧为零。只读诊断确认原固件发送命令 `0x00`、请求 1 字节，收到 `00`，SDK 返回 `ESP_OK`，随后进入面板未识别分支。

[详细报告](report.md) · [结构化结果](run.json) · [有界证据](evidence/uiflow254-gt911-panel-read.summary.json) · [此前同原版 BMI270 与 ST7123 复验](../../README.md)

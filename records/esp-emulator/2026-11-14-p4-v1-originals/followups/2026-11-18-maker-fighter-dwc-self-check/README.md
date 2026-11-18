# Tab5 Maker Fighter 1.4 在 esp-emu 1.1.0 的 USB 自检

- 日期：2026-11-18（UTC+08:00）。
- 范围：[#226](https://github.com/m5agent/m5stack-esp-emulator/issues/226) 的同原版复验，使用独立 Device Service 1.91.0 会话和 Tab5 GT911/ILI9881C 档案。
- 结果：**PASS**（只读调试冷启动确认 DWC 核心 ID 通过原固件自检）；**PARTIAL**（原应用就绪和 USB Host 功能）。
- 验证：**virtual-device validation**。物理硬件和 browser-WASM 均为 **NOT RUN**。

同一原版 BIN 的无调试试验在 42.002 秒内串口仅记录一次 ROM 启动，且无有效帧。独立的只读 PC 样本在原应用代码中观察到半字读写循环。第三次冷启动在原固件自检通过分支读得现场寄存器值 `0x4f54400a`，对应原指令从 `0x50000040` 读取的 DWC `GSNPSID`。历史断言已在这次复验中越过。USB Host 安装返回值、HID/MSC 枚举、端点传输和原应用画面仍待验收。

[详细报告和复现步骤](report.md) · [结构化结果](run.json) · [有界记录](evidence/same-bin-usb-summary.json) · [v1.0.0 复验](../../README.md)

# Maker Fighter 1.4 原版的 USB Host 安装和空端口

- 日期：2026-11-18（UTC+08:00）。
- 范围：Tab5 [#226](https://github.com/m5agent/m5stack-esp-emulator/issues/226)，同一原版 BIN，Device Service 1.92.0，esp-emu 1.1.0，GT911/ILI9881C。
- 结果：**PASS**（原版 USB Host 安装、客户端注册和进入事件等待）；**PARTIAL**（目标应用和外接 USB 数据面）。
- 验证：**virtual-device validation**。物理硬件、browser-WASM、HID/MSC 枚举和端点传输均为 **NOT RUN**。

原版函数 `usb_host_install()` 返回 `ESP_OK`。独立诊断再次运行同一固件，确认原应用进入 USB 库事件等待，USB 客户端注册也返回 `ESP_OK`。控制器 `GAHBCFG=0x21`、`HPRT=0x1000`，有 DMA 使能与根端口供电状态，连接位清零。无调试冷对照仍没有取得应用画面。

[详细报告](report.md) · [结构化结果](run.json) · [有界证据](evidence/host-setup-summary.json) · [同原版历史 GSNPSID 自检](../../README.md)

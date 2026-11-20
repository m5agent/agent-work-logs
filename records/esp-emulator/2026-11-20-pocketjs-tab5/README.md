# PocketJS 在 Tab5 原生模拟器上的兼容性

- 日期为 2026-11-20，工作类型为报告，结果为 `PARTIAL`。
- 被测版本为 PocketJS `v0.17.0` 和 Pocket M5 `v0.1.4`。环境为隔离 Device Service `1.99.5`、`esp-emu 1.1.0`、Tab5 GT911／ILI9881C 虚拟设备。

PocketJS 主仓库 ESP-IDF 示例在虚拟设备上的结果为 **PASS**。原版 Pocket M5 固件启动 Pocket Shell，实际触摸打开 `Unit Swap`、切换页面上的 `EXT 5V` 状态并返回桌面。`Tab5 Demo` 启动和音频 codec 初始化在本配置中失败。

- [复现步骤、证据与边界](report.md)
- [结构化结果](run.json)
- [虚拟设备证据摘要](evidence/virtual-device.summary.json)

未执行浏览器 WASM、真机、外接 Unit 或联网功能验收。

[2026-11-20 codec 修复与冷启动复验](followups/2026-11-20-codec-and-startup/)

[2026-11-20 自定义触控与 PCM Applet 验证](followups/2026-11-20-pulse-field/)

[2026-11-20 Port A 两种外接 Unit 虚拟验证](followups/2026-11-20-port-a-unit-swap/)

[2026-11-20 Grow Room 自定义 Applet](followups/2026-11-20-grow-room/)

[2026-11-20 Pelican Dash 触控与 Grove 走线验证](followups/2026-11-20-pelican-dash/)

# Pocket M5 Tab5 codec 与冷启动复验

- 日期为 2026-11-20，工作类型为兼容性修复，结果为 `PARTIAL`。
- 原版 Pocket M5 `v0.1.4`，Device Service `1.99.5` 与 esp-emu `1.1.0`，Tab5 GT911／ILI9881C。证据层级为 `virtual-device validation`。
- 修复通用固件导入、Tab5 音频控制总线和原版 Tab5 Demo 的启动阻断。原版成功显示硬件面板并产生 I²S1 启动音。Unit Swap 触摸与原版 UserDemo 音乐回放完成复验。
- 保留 ESP-Hosted 初始化窗口中的 P4 TLSF 断言。同版 C6 3.0.10 对照的三个冷启动会话中，两次复现断言或复位。冷启动稳定性仍待关闭。

[验证过程](report.md) · [结构化结果](run.json) · [脱敏证据](evidence/virtual-device.summary.json) · [可重放补丁](patches/0001-pocket-m5-tab5-codec-control.patch)

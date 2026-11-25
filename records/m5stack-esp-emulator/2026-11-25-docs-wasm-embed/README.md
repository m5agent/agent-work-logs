# CoreS3 和 Cardputer-Adv 文档 WASM 嵌入预研

- 日期 `2026-11-25`
- 结果 `FAIL`（正式文档页直接嵌入），`PASS`（指定的两款本地顶层编辑器控制组）
- 工作类型 `report`
- 问题来源 [M5Stack CoreS3 产品文档](https://docs.m5stack.com/en/core/CoreS3)
- 源码版本 [m5stack-esp-emulator @ afd1c635fa702b201508a5d5d689cb67ed1243f3](https://github.com/m5agent/m5stack-esp-emulator/tree/afd1c635fa702b201508a5d5d689cb67ed1243f3)
- 环境 desktop Chromium 158.0.8127.37，macOS，公开 HTTPS 文档与模拟器，以及隔离的本地静态导出

在当前正式文档页追加指向 GitHub Pages 模拟器的跨域 iframe 后，父页和子页都无法获得 WASM 所需的共享内存。子页完成 Service Worker 接管和一次额外导航，启动仍禁用。两款设备在顶层本地静态导出的 UIFlow2 控制组均完成真实来宾执行、串口双向通信、帧回传及 Worker 清理。

- [复现及范围](report.md)
- [结构化记录](run.json)
- [脱敏浏览器与固件证据](evidence/embed-and-editor-summary.json)

正式文档站部署、真机、跨浏览器兼容性和完整例程矩阵属于后续验证。

[UIFlow2 摄像头和 LoRa Cap 例程复现](followups/2026-11-25-uiflow-camera-and-lora/)

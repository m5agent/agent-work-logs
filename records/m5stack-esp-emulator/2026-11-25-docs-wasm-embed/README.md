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

逐例覆盖和演示范围见下文。正式文档托管接入、其他浏览器和真机仍待验收。

[UIFlow2 摄像头和 LoRa Cap 例程复现](followups/2026-11-25-uiflow-camera-and-lora/)

[Arduino 例程的机型探测和 Unit 复现](followups/2026-11-25-arduino-board-probe-and-units/)

[工作台隔离与 M5UI 修复回归](followups/2026-11-25-workbench-fixes/)

[UIFlow2 素材、麦克风和 CC1101 复现](followups/2026-11-25-uiflow-editor-and-cc1101/)

[UIFlow2 版本、Arduino 库和 Unit 接线对照](followups/2026-11-25-version-and-unit-controls/)

[CoreS3 ESP-IDF BSP 四个例程](followups/2026-11-25-cores3-esp-idf-bsp/)

[CoreS3 UIFlow2 ADC、GPIO、WDT、UART 示例修复](followups/2026-11-25-uiflow-sdk-example-repairs/)

[定时唤醒、RTC 和 microSD 实测](followups/2026-11-25-wakeup-and-storage/)

[已盘点的例程矩阵和演示范围](followups/2026-11-25-example-coverage/)

[ADV 板号探测回归、CoreS3 热复位及 v2.5.5 预览](followups/2026-11-25-board-probe-and-guest-reset/)

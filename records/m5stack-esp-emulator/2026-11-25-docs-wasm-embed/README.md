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

[新版 WASM 的 ADV 外设和串口复测](followups/2026-11-25-adv-new-runtime-matrix/)

[CoreS3 RTC 来宾热复位修复及 Cardputer-Adv 回归](followups/2026-11-25-cores3-rtc-reset/)

[CoreS3 BSP 黑屏修复与触摸复验](followups/2026-11-25-cores3-bsp-spi/)

[CoreS3 Music 横屏复验及三语文档发布](followups/2026-11-25-cores3-music-landscape/)

[CoreS3 Wakeup 定时休眠、唤醒及普通关机复验](followups/2026-11-25-cores3-rtc-pmic-wakeup/)

[CoreS3 与 Cardputer-Adv 文档例程 microSD 挂载复验](followups/2026-11-25-browser-demo-microsd/)

[CoreS3 UIFlow2 绘图预设与完整二维码复验](followups/2026-11-25-cores3-uiflow-display/)

## 试点结论

两款设备可以在启用浏览器跨源隔离的文档预览中演示精选例程。CoreS3 的绘图、触摸和按键，Cardputer-Adv 的显示、键盘和 Quick Start 已有真实来宾画面或输入结果。两款基准例程在桌面 Chrome 的隔离预览中约 12–24 秒到达可操作状态。窄屏使用完整工作台时，启动按钮在内层页面顶部以下约 1,900 CSS px。建议试点提供模拟屏幕和必要的控件，在实际应用画面出现后启用输入。[逐例矩阵与交互观察](followups/2026-11-25-example-coverage/)

## 修复状态

| 改动 | 截至 2026-11-25 的状态 |
| --- | --- |
| 工作台隔离提示和 CoreS3 UIFlow2 M5UI 事件处理 | 已合入模拟器主分支，隔离预览中复验。[模拟器 PR #251](https://github.com/m5agent/m5stack-esp-emulator/pull/251) |
| Cardputer-Adv WASM 板型探测 | 已合入模拟器主分支。重建 WASM 上复验原显示、键盘和 Quick Start。正式托管版本待更新。[模拟器 PR #256](https://github.com/m5agent/m5stack-esp-emulator/pull/256) |
| CoreS3 ESP-IDF BSP 显示与 Music | WASM 显示修复已合入。Music 分区与横屏配置已发布中、英、日三语说明，浏览器通过横屏播放器触摸复验。[正式文档](https://docs.m5stack.com/en/esp_idf/m5cores3/bsp) |
| CoreS3 来宾热复位 | WASM 修复已合入。原 UIFlow2 WDT 和软件复位恢复新控制台代次及程序执行。[模拟器 PR #259](https://github.com/m5agent/m5stack-esp-emulator/pull/259) |
| CoreS3 UIFlow2 ADC、GPIO、WDT 和 UART 例程修正 | 在同一 WASM 路径复验，待上游合并。[UIFlow2 PR #132](https://github.com/m5stack/uiflow-micropython/pull/132) |

## 后续问题

| 范围 | 已建 Issue |
| --- | --- |
| 正式文档 iframe 和例程配置 | [跨源隔离 #242](https://github.com/m5agent/m5stack-esp-emulator/issues/242)、[microSD 素材 #253](https://github.com/m5agent/m5stack-esp-emulator/issues/253)、[附件、网络对端与 Blockly #255](https://github.com/m5agent/m5stack-esp-emulator/issues/255) |
| 画面和运行时 | [ADV 托管运行时更新 #245](https://github.com/m5agent/m5stack-esp-emulator/issues/245)、[CoreS3 UIFlow2 版本与裁切 #249](https://github.com/m5agent/m5stack-esp-emulator/issues/249)、[CoreS3 ESP-IDF 黑屏 #250](https://github.com/m5agent/m5stack-esp-emulator/issues/250) |
| CoreS3 外设和电源管理 | [摄像头 #243](https://github.com/m5agent/m5stack-esp-emulator/issues/243)、[超声波与继电器 #246](https://github.com/m5agent/m5stack-esp-emulator/issues/246)、[播放器与麦克风 #248](https://github.com/m5agent/m5stack-esp-emulator/issues/248)、[定时唤醒 #252](https://github.com/m5agent/m5stack-esp-emulator/issues/252)、[WDT 与软件热复位 #254](https://github.com/m5agent/m5stack-esp-emulator/issues/254) |
| Cardputer-Adv 外设和串口 | [LoRa 与 GNSS #244](https://github.com/m5agent/m5stack-esp-emulator/issues/244)、[CC1101 #247](https://github.com/m5agent/m5stack-esp-emulator/issues/247)、[USB CDC 按键日志 #257](https://github.com/m5agent/m5stack-esp-emulator/issues/257)、[IR NEC #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258)、[上游 NFC 构造器 #131](https://github.com/m5stack/uiflow-micropython/issues/131) |

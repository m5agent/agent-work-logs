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

[CoreS3 QVGA 摄像头 DMA 修复与原例程复验](followups/2026-11-25-cores3-qvga-camera/)

[CoreS3 超声波与继电器原例程自动挂接复验](followups/2026-11-25-cores3-unit-examples/)

[Cardputer-Adv 两份 LoRa Cap GPS 原例程与 UART2 定位](followups/2026-11-25-cardputer-adv-gnss/)

[CoreS3 I²S 原例程文件播放、录放及节拍诊断](followups/2026-11-25-cores3-audio-dma-diagnostics/)

[Cardputer-Adv USB Serial/JTAG 输出、IR 和 Button 对照](followups/2026-11-25-cardputer-adv-usb-cdc/)

[Cardputer-Adv CC1101 原收发例程的双来宾预览](followups/2026-11-25-cardputer-adv-cc1101-peer/)

[Cardputer-Adv LoRa1262 与 LoRa868 原收发例程的 SX1262 双来宾预览](followups/2026-11-25-cardputer-adv-sx1262-peer/)

[Cardputer-Adv IR NEC 原例程的文档横屏修正](followups/2026-11-25-cardputer-adv-ir-landscape/)

[Cardputer-Adv 默认 CDC 的 Button 原例程三次复验](followups/2026-11-25-cardputer-adv-button-default-cdc/)

[Cardputer-Adv CC1101 标准工作台双标签页收发](followups/2026-11-25-cardputer-adv-cc1101-workbench/)

[Cardputer-Adv IR 原例程竖屏方向与 GPIO44 时序对照](followups/2026-11-25-cardputer-adv-ir-portrait-and-timing/)

[Cardputer-Adv LoRa1262 与 LoRa868 标准工作台双标签页收发](followups/2026-11-25-cardputer-adv-sx1262-workbench/)

[Cardputer-Adv 原 Button 五次冷启动，保留超时和线程异常](followups/2026-11-25-cardputer-adv-button-cold-start/)

[CoreS3 Arduino 卡载 WAV 与 UIFlow2 麦克风完成浏览器音频复验](followups/2026-11-25-cores3-browser-audio/)

[Cardputer-Adv Button 正常与单指令调度冷启动对照](followups/2026-11-25-cardputer-adv-button-oneinsn/)

[CoreS3 原 M5Switch 与 Slider 的真实触控、画面和中断](followups/2026-11-25-cores3-stock-m5ui/)

[CoreS3 两份 Blockly 原工程的官方生成、来宾阻塞和 M5Arc 源码对照](followups/2026-11-25-cores3-blockly-source-preview/)

[Cardputer-Adv 锁定 WASM 的竖屏、显示、键盘和四种旋转](followups/2026-11-25-cardputer-adv-signed-portrait-locked-0049/)

[CoreS3 DualKmeter 原例程三组有符号温度及实际 I²C](followups/2026-11-25-cores3-dual-kmeter-private/)

[Cardputer-Adv NFC Cap 构造器、真实 SPI 与原例程画面](followups/2026-11-25-nfccap-sdk-131/)

[Cardputer-Adv 两份 IR 原例程的确定性时钟与严格 NEC 解码](followups/2026-11-25-cardputer-adv-ir-private-icount/)

[Cardputer-Adv 原 Button 单线程指令计数的三次冷启动](followups/2026-11-25-cardputer-adv-button-icount/)

[CoreS3 DualKmeter 标准工作台原例程、温度控件及同镜像负对照](followups/2026-11-25-cores3-dual-kmeter-workbench/)

## 本轮复验结论

两款设备可用选定的原例程做交互演示。CoreS3 已复验图形、触控、四个 BSP 界面、相机的虚拟画面、microSD 图片、RTC 定时唤醒和若干外设。卡载 WAV 和虚拟麦克风有浏览器数字音频输出，DualKmeter 在标准工作台有实际 I²C 温度读数。Cardputer-Adv 已复验原显示、键盘、microSD、CC1101 和两种 LoRa Cap 的双来宾收发，以及两种 GNSS 原例程的 UART2 定位。不同案例各自绑定固定固件、素材和启动配置。

初次盘点覆盖 15 个 CoreS3 Arduino、11 个 Cardputer-Adv Arduino、4 个 CoreS3 ESP-IDF BSP 例程，以及明确标注板型的 208 个 UIFlow2 Python 和 2 个仅有 Blockly 工程的例程。初测时 109 个附件例程因缺数据路径未送入来宾。两份 Blockly 都已用官方编辑器生成原 Python 并实跑，DualKmeter 现已通过，ModuleLLM 仍需要 UART2 对端。[初次逐例矩阵](followups/2026-11-25-example-coverage/) · [Blockly 复验](followups/2026-11-25-cores3-blockly-source-preview/)

选定基准在本地桌面 Chromium 约 12–24 秒到可交互画面。部分例程仍有专属条件。M5Switch 的可见触点使用显式 v2.5.5，CoreS3 音频需要显式启用，两份 IR 固件的严格 NEC 校验使用私有确定性配置，Button 的冷启动仍有可复现失败。正式文档嵌入、Pages 部署、其他浏览器及真机由后续独立验收。[M5UI 触点](https://github.com/m5agent/m5stack-esp-emulator/issues/273) · [原 Speaker 素材](https://github.com/m5agent/m5stack-esp-emulator/issues/271) · [ModuleLLM](https://github.com/m5agent/m5stack-esp-emulator/issues/274) · [IR 时序](https://github.com/m5agent/m5stack-esp-emulator/issues/258) · [Button](https://github.com/m5agent/m5stack-esp-emulator/issues/268) · [附件、网络及例程矩阵](https://github.com/m5agent/m5stack-esp-emulator/issues/255)

## 试点结论

两款设备可以在启用浏览器跨源隔离的文档预览中演示精选例程。CoreS3 的绘图、触摸和按键，Cardputer-Adv 的显示、键盘和 Quick Start 已有真实来宾画面或输入结果。两款基准例程在桌面 Chrome 的隔离预览中约 12–24 秒到达可操作状态。窄屏使用完整工作台时，启动按钮在内层页面顶部以下约 1,900 CSS px。建议试点提供模拟屏幕和必要的控件，在实际应用画面出现后启用输入。[逐例矩阵与交互观察](followups/2026-11-25-example-coverage/)

## 修复状态

| 改动 | 截至 2026-11-25 的状态 |
| --- | --- |
| 工作台隔离提示和 CoreS3 UIFlow2 M5UI 事件处理 | 已合入模拟器主分支，隔离预览中复验。[模拟器 PR #251](https://github.com/m5agent/m5stack-esp-emulator/pull/251) |
| Cardputer-Adv WASM 板型探测 | 已合入模拟器主分支。重建 WASM 上复验原显示、键盘和 Quick Start。正式托管版本待更新。[模拟器 PR #256](https://github.com/m5agent/m5stack-esp-emulator/pull/256) |
| CoreS3 ESP-IDF BSP 显示与 Music | WASM 显示修复已合入。Music 分区与横屏配置已发布中、英、日三语说明，浏览器通过横屏播放器触摸复验。[正式文档](https://docs.m5stack.com/en/esp_idf/m5cores3/bsp) |
| CoreS3 来宾热复位 | WASM 修复已合入。原 UIFlow2 WDT 和软件复位恢复新控制台代次及程序执行。[模拟器 PR #259](https://github.com/m5agent/m5stack-esp-emulator/pull/259) |
| CoreS3 超声波与继电器 | 原例程在本地浏览器工作台通过自动挂接、I²C/GPIO、画面与停止验证。[复验](followups/2026-11-25-cores3-unit-examples/) |
| CoreS3 UIFlow2 ADC、GPIO、WDT 和 UART 例程修正 | 在同一 WASM 路径复验，待上游合并。[UIFlow2 PR #132](https://github.com/m5stack/uiflow-micropython/pull/132) |

## 后续问题

| 范围 | 已建 Issue |
| --- | --- |
| 正式文档 iframe 和例程配置 | [跨源隔离 #242](https://github.com/m5agent/m5stack-esp-emulator/issues/242)、[microSD 素材 #253](https://github.com/m5agent/m5stack-esp-emulator/issues/253)、[附件、网络对端与 Blockly #255](https://github.com/m5agent/m5stack-esp-emulator/issues/255) |
| 画面和运行时 | [ADV 托管运行时更新 #245](https://github.com/m5agent/m5stack-esp-emulator/issues/245)、[CoreS3 UIFlow2 版本与裁切 #249](https://github.com/m5agent/m5stack-esp-emulator/issues/249)、[CoreS3 ESP-IDF 黑屏 #250](https://github.com/m5agent/m5stack-esp-emulator/issues/250) |
| CoreS3 外设和电源管理 | [播放器与麦克风 #248](https://github.com/m5agent/m5stack-esp-emulator/issues/248) |
| Cardputer-Adv 外设和串口 | [LoRa 与 GNSS #244](https://github.com/m5agent/m5stack-esp-emulator/issues/244)、[CC1101 #247](https://github.com/m5agent/m5stack-esp-emulator/issues/247)、[USB CDC 按键日志 #257](https://github.com/m5agent/m5stack-esp-emulator/issues/257)、[IR NEC #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258)、[上游 NFC 构造器 #131](https://github.com/m5stack/uiflow-micropython/issues/131) |

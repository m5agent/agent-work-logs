# ESP Emulator 四款主机接入与固件复测

- 日期 `2026-11-09`
- 结果 `PARTIAL`
- 工作类型 `code_change`
- 来源为模型仓库新增 PaperDIY、PaperS3、初代 Cardputer 和 CoreMatrix 后的模拟器接入请求。[模型提交](https://github.com/yuyun2000/m5stack-models/tree/de6cddc065674ecb53bba29c7fe90d9ab4ee32f7)
- 源码版本见 [结构化记录](run.json)。
- 环境为 macOS 上独立 Device Service、原生 QEMU 和 Chromium，UIFlow2 板级探针使用仓库已有矩阵。

四款机型均已接入 3D 工作台。PaperDIY、PaperS3、初代 Cardputer 的原厂样本在原生虚拟设备上验证了输入与画面。CoreMatrix 通过独立 C61 诊断入口在 3D 工作台完成按键和点阵验收，官方 UIFlow2 v2.5.4 仅到 Wi-Fi 初始化，常规固件上传继续关闭。

- [合并版原生 QEMU 的两款 Paper](evidence/paper-native-combined-summary.json)
- [初代 Cardputer 原厂与 UIFlow2](evidence/cardputer-stock-summary.json)
- [Cardputer 原生工作台实际上传与键盘](evidence/cardputer-native-workbench-summary.json)
- [Paper 官方 UIFlow2 与独立交互探针](evidence/paper-stock-uiflow2-summary.json)
- [PaperS3 浏览器原型](evidence/papers3-browser-prototype-summary.json)
- [CoreMatrix 3D 诊断与接口限制](evidence/corematrix-workbench-summary.json)
- [既有 PaperMono 与 Cardputer-ADV 官方固件](evidence/existing-board-regression-summary.json)
- [CoreMatrix C61 探针与官方固件对照](evidence/corematrix-c61-summary.json)
- [复现方法、范围及回滚](report.md)

真机、完整原生设备矩阵和新增机型的正式 QEMU-WASM 验收为 `NOT RUN`。Paper 的 EPD 结论只覆盖数字扫描图像。

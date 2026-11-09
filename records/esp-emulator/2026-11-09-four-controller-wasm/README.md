# ESP Emulator 四款设备浏览器 WASM 与 CoreMatrix 官方启动

- 日期 2026-11-09
- 结果 `PARTIAL`，各固件和交付层分别记载。
- 类型 code_change
- 来源为四款原生模拟器接入的后续验收和 GitHub Pages 更新。[原生接入](https://github.com/m5agent/m5stack-esp-emulator/pull/197)
- 源码起点为 `m5agent/m5stack-esp-emulator` @ `e9bb9f2efa5201e024715dedd5152b54086f6a59`。
- 环境为原生 Device Service、Chromium、本地 Xtensa 与 RISC-V C/QEMU WASM。

CoreMatrix C158 使用未改动的官方 UIFlow2 v2.5.4。修复计数器、PHY 初始化、软件 I²C、显示供电和 USB Serial/JTAG 后，原生运行显示 36 像素的未配置网络标识，USB REPL 可绘制和读取输入。最终 C61 浏览器构建通过相同原版镜像和官方基底衍生的编程、按键与固定示例。初代 Cardputer 的 Factory V0.9 和 UIFlow2 v2.5.4 原镜像通过最终 Xtensa 构建。两款 Paper 均通过原厂应用、编辑器、输入和固定示例。发布层单独记载。

- [CoreMatrix 原生 stock 启动、矩阵、按键与串口](evidence/corematrix-native-stock-summary.json)
- [CoreMatrix 浏览器诊断与先前失败](evidence/corematrix-provisional-browser-summary.json)
- [CoreMatrix 浏览器原镜像和三个组合示例](evidence/corematrix-browser-qualification-summary.json)
- [初代 Cardputer 浏览器两份原镜像](evidence/cardputer-browser-qualification-summary.json)
- [两款 Paper 浏览器固件、输入与清理](evidence/paper-browser-qualification-summary.json)
- [PaperS3 Factory V0.5 的 300 毫秒触控](evidence/papers3-factory-short-touch-summary.json)
- [实现与边界](report.md)
- [结构化执行](run.json)

实体硬件、CoreMatrix 8 MiB Quad PSRAM、Wi-Fi 数据面及浏览器硬件复位仍待验收。

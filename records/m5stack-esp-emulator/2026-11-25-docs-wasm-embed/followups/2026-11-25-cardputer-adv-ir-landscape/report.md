# 复现与范围

英语、简体中文和日语的示例共用原 Arduino 源码。Cardputer-Adv 在实际使用的 M5Cardputer 1.1.1、M5GFX 0.3.0 中，例程的 `setRotation(1)` 使逻辑屏宽 135 像素。使用 Orbitron Light 24 时，“IR NEC SEND”约需 180 像素。此前原固件的平面浏览器页面确实显示倒置与裁切。[相同浏览器 USB 与原固件对照](../2026-11-25-cardputer-adv-usb-cdc/)

原有旋转设置之后仅增加三行。若实际宽度小于高度，调用 `setRotation(0)`。确认三语 Markdown 的 C++ 代码块与浏览器复验的源文件字节一致。工作台实际 240×135 的平面画面没有 CSS 旋转，三行 `IR NEC SEND`、`ADDR:0x1111`、`CMD:0x35` 可完整阅读。来宾从实际虚拟 USB 控制器分别输出 `0x34` 和 `0x35`，控制器累计 435 字节、38 包。测试同次会话正常退出 0，6 个 Worker 全部回收。

1. 取三语任一官方 [IR NEC 例程](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec) 的改后源码，摘要 `6d3d4ae7a3f4a2988495735ab8bd36b4e2f92324515fba15fcefd757c65b9df5`。
2. 用 Arduino CLI 1.3.1、M5Stack Arduino 3.2.5，默认 `m5stack:esp32:m5stack_cardputer` 选项编译。库版本 M5Cardputer 1.1.1、M5Unified 0.3.0、M5GFX 0.3.0 和 Arduino-IRremote 4.7.1。核对 4 MiB 合并镜像 `ae81222c…afdb` 及在模拟器补齐至 8 MiB 后的摘要 `69d9f658…093f`。
3. 用浏览器工作台选择 Cardputer-Adv，上传镜像，观察平面屏幕并选择 USB Serial/JTAG 输出。核对三个文字字段、两条实际应用命令和正常清理。WASM `ee110d20…cc60`，完整锁和哈希见[执行摘要](evidence/landscape.summary.json)。

该轮修复和验收针对 Cardputer-Adv 的例程画面。初代 Cardputer、物理红外与 USB、GPIO44 的 LEDC 波形，以及工作台对任意客体竖屏方向的处理未执行。

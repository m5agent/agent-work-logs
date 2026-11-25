# UIFlow2 版本和 Arduino/Unit 固件对照

- 日期 `2026-11-25`
- 结果 `PASS`（指定的旧版库、版本对照和 Unit 原型），`FAIL`（ADV 新版 SDK NFC 构造），`PARTIAL`（默认浏览器接入）
- 工作类型 `report`
- 来源 [Cardputer-Adv Arduino](https://docs.m5stack.com/en/arduino/m5cardputer/program) · [CoreS3 UIFlow2 显示](https://uiflow-micropython.readthedocs.io/en/latest/hardware/display.html) · [CC1101 Cap](https://uiflow-micropython.readthedocs.io/en/latest/cap/cc1101.html)
- 源码 [m5stack-esp-emulator @ afd1c635fa702b201508a5d5d689cb67ed1243f3](https://github.com/m5agent/m5stack-esp-emulator/tree/afd1c635fa702b201508a5d5d689cb67ed1243f3)
- 环境 Chrome 158.0.8127.37、macOS、浏览器 WASM 虚拟设备验证

Cardputer-Adv 使用文档所列最低 Arduino 库和 8 MiB 配置完成图形和键盘例程。CoreS3 用实际端口挂接 Relay、Ultrasonic-I2C 后通过原例程的控制器和屏幕双验。官方 UIFlow2 v2.5.5 的 CoreS3 绘图对照渲染了完整二维码，ADV v2.5.5 的 NFC 构造对照仍报关键字类型错误。

- [条件与复现](report.md)
- [结构化记录](run.json)
- [Unit 和 Arduino 对照](evidence/arduino-and-unit-controls-summary.json)
- [UIFlow2 版本对照](evidence/uiflow225-version-summary.json)

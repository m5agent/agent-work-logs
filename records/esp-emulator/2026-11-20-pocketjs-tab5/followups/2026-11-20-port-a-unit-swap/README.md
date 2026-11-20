# Tab5 Pocket M5 Port A 外接 Unit 验证

2026-11-20 · 工程报告 · `PARTIAL`

原版 [Pocket M5 v0.1.4](https://github.com/pocket-nexus/pocket-m5/releases/tag/v0.1.4) 的 Unit Swap 在 Tab5 虚拟设备中识别 ENV III 和 Ultrasonic-I2C，经 GPIO53/54 组成的 Port A 软件 I²C 读取它们。两种 Unit 在同一会话先后连接，温湿度、气压与超声波读数从来宾屏幕回读。拔下 ENV III 后，Applet 回到等待状态，再识别 0x57 的超声波 Unit。

- [复现及配置边界](report.md)
- [结构化结果](run.json)
- [控制器、串口与帧证据](evidence/virtual-device.summary.json)
- [隔离采集配置补丁](patches/0001-tab5-port-a-unit-capture.patch)

证据层级为 `virtual-device validation`。该次会话在 Applet 就绪前出现一次 P4 TLSF 断言复位。真机、浏览器 WASM、RFID 及其余 Unit 均未测试。

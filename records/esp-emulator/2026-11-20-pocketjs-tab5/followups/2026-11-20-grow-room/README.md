# Grow Room Tab5 Applet 虚拟设备验证

2026-11-20 · 工程报告 · `PARTIAL`

新编写的 PocketJS 温室 Applet 通过原版 Pocket M5 v0.1.4 启动器运行。来自同一次原生 Tab5 会话的 GPIO/软件 I²C、串口和屏幕证据确认两条路径。改变 ENV III 的环境输入后，Applet 实际读取 34.0 °C、38% RH 并发出高温提示。换成超声波 Unit 后，模拟补水使 Applet 的储水量从 28% 变为 82%。

- [重放方法与验证边界](report.md)
- [结构化记录](run.json)
- [同一会话证据](evidence/virtual-device.summary.json)

该次原生会话在 Applet 就绪前出现一次 TLSF 断言复位。真机、浏览器 WASM、实际水箱及联网安装未验证。

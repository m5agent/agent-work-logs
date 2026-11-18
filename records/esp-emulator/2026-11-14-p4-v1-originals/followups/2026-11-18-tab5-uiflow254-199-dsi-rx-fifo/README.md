# Tab5 UIFlow2 v2.5.4 的 DSI RX FIFO 复验

- **日期** 2026-11-18
- **结论** PARTIAL，virtual-device validation
- **类型** issue
- **对象** [Tab5 #188](https://github.com/m5agent/m5stack-esp-emulator/issues/188)
- **源码** esp-emulator `218106fa` 的执行源码与 Device Service 1.99 发布版 `a729e24b` 一致
- **环境** macOS arm64、原生 esp-emu 1.1.0、独立虚拟 Device Service

用同一份原版 UIFlow2 v2.5.4，在 Device Service 1.99 和 esp-emu 1.1.0 上分别启动 GT911／ILI9881C 与 ST7123。GT911 普通启动无完整帧。独立诊断观察到原版 CPU 从 DSI RX FIFO 取到零，面板 ID 比较失败。ST7123 普通启动出帧，真实触控报告把界面切到 I²C Scan。

官方 1.1.0 将 DSI 读请求通知面板消费者，由后端自行以零完成读回。GT911 关闭条件仍需接通同步面板读响应与 FIFO，再复验原版冷启动、画面、实际触摸和应用执行。[Espressif 1.1.0 发布记录](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) · [固定版 co-sim 协议](https://github.com/espressif/esp-emulator/blob/v1.1.0/proto/esp_cosim.proto#L1018-L1045)

- [完整报告](report.md)
- [运行身份和检验项](run.json)
- [精简机器证据](evidence/dsi-rx-fifo.summary.json)
- [只读指令观测脚本](code/fifo_probe.py)

真机、浏览器、联网、配对、应用脚本执行及非零面板回包正对照为 NOT RUN。Burner 未提交。

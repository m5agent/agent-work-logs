# 官方 UIFlow2 摄像头和 LoRa Cap 例程

- 日期 `2026-11-25`
- 结果 `FAIL`（CoreS3 摄像头帧长与 Cardputer-Adv LoRa 收发），`PARTIAL`（GNSS 页面）
- 工作类型 `report`
- 来源 [Camera 示例](https://uiflow-micropython.readthedocs.io/en/latest/advanced/camera.html) · [LoRa1262 Cap](https://uiflow-micropython.readthedocs.io/en/latest/cap/lora1262.html) · [LoRa868 Cap](https://uiflow-micropython.readthedocs.io/en/latest/cap/lora868.html)
- 源码 [m5stack-esp-emulator @ afd1c635fa702b201508a5d5d689cb67ed1243f3](https://github.com/m5agent/m5stack-esp-emulator/tree/afd1c635fa702b201508a5d5d689cb67ed1243f3)
- 环境 Chrome 158.0.8127.37，macOS，本地静态导出，浏览器 WASM 虚拟设备验证

CoreS3 原例程请求 RGB565 QVGA。320×240 屏幕出现虚拟场景，串口持续报告相机缓冲区长度不符。Cardputer-Adv 原例程出现 SX126x BUSY 超时。GNSS 例程能画出初始界面，这轮未达成定位数据刷新。

- [复现与证据](report.md)
- [结构化记录](run.json)
- [脱敏来宾摘要](evidence/camera-and-lora-summary.json)

真机、光学与 RF 验证 `NOT RUN`。

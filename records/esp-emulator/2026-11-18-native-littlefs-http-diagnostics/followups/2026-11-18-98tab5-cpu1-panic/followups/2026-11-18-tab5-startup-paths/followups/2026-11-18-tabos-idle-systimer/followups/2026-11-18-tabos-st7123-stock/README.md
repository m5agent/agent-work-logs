# M5TabOS 原版的 Tab5 板型、出帧与触摸

- 日期为 2026-11-18。结果为 PASS，覆盖 ST7123 配置下的原版启动显示和一次触摸。
- 固件为 M5TabOS 0.9.1 原版。环境为隔离 Device Service 1.90.0 和 Tab5 原生 esp-emu 1.1.0。
- 验证类型为 virtual-device validation。机器和镜像固定版本及 SHA-256 见回执。

同一原版在两种 GT911 接法均会完成应用的启动标记，但保留 0×0 的显示对象并无有效帧。ST7123 识别部件已足以启动显示，完整触摸部件的无调试启动和欢迎页单击翻页也通过。实际 GPIO23 与 I²C 记录显示按下和抬起均被来宾读取。[报告](report.md) · [执行清单](run.json) · [验证回执](evidence/tabos-stock-board-touch.summary.json)

# Cardputer-Adv LoRa Cap 定位原例程

- 日期 2026-11-25
- 类型 fix，virtual-device validation
- 平台 Cardputer-Adv，Chromium 156.0.8078.4
- 问题 [模拟器 #244](https://github.com/m5agent/m5stack-esp-emulator/issues/244)

LoRa1262 和 LoRa868 的原 GPS 程序分别在浏览器工作台通过。地点 A/B 各有 423 字节经真实虚拟 UART2 读入，来宾屏幕显示预期经纬度和时间。默认工作台使用同一固件时保持普通键盘和串口路径。三次运行正常关闭全部 Worker。

- [对照、原程序和复现](report.md)
- [结构化执行记录](run.json)
- [串口参数、输入回执、RGB565 和回收](evidence/standard-workbench.summary.json)

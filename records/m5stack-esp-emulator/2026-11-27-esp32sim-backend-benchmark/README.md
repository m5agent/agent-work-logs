# esp32sim 与封存后端同固件对照

- 日期 `2026-11-27`
- 工作类型 `report`
- 结果 `PARTIAL`，原生和浏览器均为 virtual-device validation
- 源码 `m5agent/m5stack-esp-emulator@16faae71c3ee67f5158431dbe78c27e726e67d3d`
- 原生 esp32sim `m5agent/esp32sim@4e257b6be8ee0ed706c2e509d8f31ef7472a424b`
- 样本来源为 Arduino 产品文档、M5Burner 原版 UIFlow2 和旧缺口的精确固件。
  [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188) · [#226](https://github.com/m5agent/m5stack-esp-emulator/issues/226) · [#242](https://github.com/m5agent/m5stack-esp-emulator/issues/242)

浏览器 CoreS3 Touch 从 4.380 s 降到 1.675 s，ADV Keyboard 从 5.081 s
降到 2.076 s。两个场景各有三次成对运行，全部清理 Worker。
原生的启动、CPU、RSS 和输入结果随板卡及固件变化。

- [完整报告与命令](report.md)
- [结构化执行记录](run.json)
- [原生逐次脱敏回执](evidence/native-summary.json)
- [浏览器逐次脱敏回执](evidence/browser-summary.json)
- [复现脚本](code/)

原始抓取只留在运行工作区。公开回执保留哈希和测量值，省略会话标识、宿主进程、
环境路径、串口原文及含设备身份的画面。正式文档部署和物理硬件未验收。

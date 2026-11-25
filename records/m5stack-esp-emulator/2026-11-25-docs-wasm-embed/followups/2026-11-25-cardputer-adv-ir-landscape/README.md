# Cardputer-Adv IR NEC 文档例程的横屏显示

- 日期 2026-11-25
- 类型 documentation bug fix，virtual-device validation
- 设备 Cardputer-Adv，Chrome 158.0.8127.37
- 问题 [IR 原例程 #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258)

在选定 SDK 上，原例程设定的旋转会形成 135 像素宽的逻辑屏幕，标题、地址及命令文字被裁切。改动在逻辑宽度小于高度时切换横屏。实际 240×135 画面显示完整标题、地址与命令，原应用仍经 USB 报告递增命令。

- [对照、源和复现步骤](report.md)
- [结构化执行记录](run.json)
- [来宾原生帧、实际 USB 及清理](evidence/landscape.summary.json)
- [三语官网发布后回读](evidence/delivery.summary.json)

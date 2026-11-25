# Cardputer-Adv 浏览器 USB Serial/JTAG CDC 输出

- 日期 2026-11-25
- 类型 fix，virtual-device validation
- 设备 Cardputer-Adv，浏览器 WASM
- 问题 [USB 按键 #257](https://github.com/m5agent/m5stack-esp-emulator/issues/257) · [IR 原例程 #258](https://github.com/m5agent/m5stack-esp-emulator/issues/258)

复用虚拟 USB Serial/JTAG 的 IN FIFO、完成中断和主机调度，工作台独立显示设备 USB 输出。原 IR 例程在同一会话经 USB 报告地址及两个命令。关 CDC 的原按键对照仍从 UART0 返回应用按下和释放。默认 CDC 的按键固件未得到应用报文。IR 竖屏预览的方向和裁切、GPIO44 LEDC 包络继续跟踪。

- [可复现的测试、失败和边界](report.md)
- [结构化执行记录](run.json)
- [锁定构建、实际控制器、可见帧和停止](evidence/browser-examples.summary.json)

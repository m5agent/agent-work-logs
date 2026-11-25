# CoreS3 ESP-IDF BSP 的 WASM 黑屏修复

- 日期 2026-11-25
- 工作类型 fix，virtual-device validation
- 结果 PASS，覆盖四个原 BSP 例程的显示与 Widgets 触摸
- 设备 CoreS3，Chrome 158.0.8127.37，Apple Silicon macOS
- 问题来源 [模拟器 #250](https://github.com/m5agent/m5stack-esp-emulator/issues/250)
- 源码基线 8f727c0b0d9defe6b50647425064a91288dc1b7c，候选 35c46e112ffa7f1a52b03e8a3c5c5b84f677922d
- 真机、原生及正式托管验证 NOT RUN

四个原 CoreS3 BSP 例程在完整源构建 WASM 上恢复显示。同会话用触摸坐标在 Widgets 的 Profile 和 Analytics 来回切换，实际像素由人物头像切换为访客曲线再返回。旧运行时的同固件黑屏和 GDMA 空传输有独立负控。

- [分析、配线和复验过程](report.md)
- [结构化执行记录](run.json)
- [四个 BSP 例程显示证据](evidence/esp-idf-bsp-display.summary.json)
- [旧运行时、单项调整、完整候选的三组总线对照](evidence/gdma-and-chip-select.summary.json)
- [锁定 WASM 的 Widgets 触摸及清理](evidence/widgets-touch.summary.json)
- [挂接实际 FAT 的 SD/Picture 同路线回归](evidence/cores3-attached-sd-regression.summary.json)
- [Cardputer-Adv 键盘与显示回归](evidence/cardputer-adv-regression.summary.json)

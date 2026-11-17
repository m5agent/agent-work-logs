# Tab5 ST7123 无 ELF 单点拖动

- 日期 `2026-11-17`
- 结果 `PASS`（同触点数据面、释放和原输入回归）
- 类型 `code_change`
- 来源 Tab5 原生可审核输入
- 版本 `m5stack-esp-emulator @ 4160e5d27732742052e2246bffb773a718373ca6`
- 环境 隔离 Device Service、原生 ESP32-P4、编译固定的 ST7123 Part

实际来宾从 GPIO23 和 HP I²C1 读取正反向各六个连续坐标和一次释放，控制器均有 7/7 确认。原版 Arduventure 的点击及 1.2 秒长按与原版 CarPlay 的 GT911 回归通过。独立冻结包重跑了正反向、空闲与旧输入对照。

- [复现和证据边界](report.md)
- [结构化记录](run.json)
- [原生数据面和原版对照](evidence/native-drag-summary.json)
- [冻结包重放](evidence/combined-drag-summary.json)

原版应用在 ST7123 的拖动语义、多点触控、浏览器、整机关机和物理硬件仍待各自验证。未提交 Burner。

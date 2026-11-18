# Cardputer NC1020 原版停刷的两个 SPI 等待现场

- 日期为 2026-11-19（UTC+08:00）。
- 结果为 `PARTIAL`。原版的两个停刷现场均复现，存档恢复和已重建对照的完整画面通过。
- 工作类型为同路径虚拟设备诊断，延续 [原版 1.99.0 冷启动回读](../../README.md)。
- 环境为 Device Service 1.99.0、原生 QEMU Xtensa 和 Cardputer K132。三个独立工作器使用相同的原生运行时、ROM 与 FAT32。
- 源码为 `m5stack-esp-emulator @ 981fdcdf09253b75be960772147258b677775d8c`。 [固定版本 API](https://github.com/m5agent/m5stack-esp-emulator/blob/981fdcdf09253b75be960772147258b677775d8c/docs/device-service-api.md)

原版两轮都停在空的 SPI 总线锁信号量上。其中一轮 SPI 完成队列和 LCD 在途计数均为 0，另一轮均为 1。已有的 ESP-IDF 修订重建对照得到完整图案，LCD 完成绘制后回到等待下一帧，两种停刷形态与正常空闲可从真实队列和帧区分。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏证据摘要](evidence/nc1020-199-spi-wait.summary.json)

本次读取了已发生停刷后的现场，当前 1.99.0 上的双核交接顺序与物理设备均为 `NOT RUN`。这次没有重建或修改任何固件。

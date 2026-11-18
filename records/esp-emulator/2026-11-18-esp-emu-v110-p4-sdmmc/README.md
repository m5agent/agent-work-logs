# ESP-EMU 1.1.0 P4 SDMMC 接入评估

- 日期为 2026-11-18（UTC+08:00）。
- 结果为 `PASS`（P4 SDMMC 驱动和 FAT 数据面）及 `NOT RUN`（Tab5 板级接入）。
- 工作类型为报告与虚拟设备验证。
- 对照 [ESP-EMU v1.1.0](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0) 与 [项目 main](https://github.com/m5agent/m5stack-esp-emulator/tree/174c6d42048bf12f315e8b572948f17638d0bb77)。
- 环境为 Apple Silicon macOS、原生 ESP-EMU v1.1.0、P4 rev3.1 和 ESP-IDF v5.5.4 示例。

同一例程在有卡时挂载 FAT16、写入并读回两个文件。进程退出后，宿主从镜像文件系统读出对应字节。空槽发生初始化超时，只读挂载后的写入被拒且镜像逐字节保持一致。该结果支持为 Tab5 的原生候选后端增加会话私有 SD 镜像。

- [完整对照、接入边界和复现命令](report.md)
- [运行身份和验收层级](run.json)
- [串口标记、文件内容和完整 SHA-256](evidence/sdmmc-summary.json)

Tab5 原版、slot 0 和 ESP-Hosted 并行、Device Service 接入与复位后重挂载待验证。无浏览器或实机执行。

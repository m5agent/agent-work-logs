# PaperDIY 原生 SD 热插拔

- 日期 2026-11-17
- 结果 `PASS`，virtual-device validation
- 工作类型 `code_change`
- 问题来源 PaperDIY 在固件审核会话中只能开机挂卡
- 源码候选 `563d4debf6ae11f4bd4092aba920f56aa82df772`
- 环境 独立 Device Service、native Xtensa QEMU 与 ESP-IDF v5.5.4 来宾

同一来宾从空卡槽启动，经历插卡、拔卡、重新插卡与拔卡。四次 GPIO48
中断各执行一次。FAT32 首次插卡读写成功，拔卡后无法挂载，再插入读回
已写文件。停止后镜像导出哈希与独立 FAT 检查一致。

- [报告](report.md)
- [结构化记录](run.json)
- [脱敏证据](evidence/paperdiy-sd-hotplug-summary.json)
- [复现与 16 MiB 夹具](https://github.com/m5agent/m5stack-esp-emulator/blob/563d4debf6ae11f4bd4092aba920f56aa82df772/tests/firmware/spi_sd_media/README.md#paperdiy-sd-hot-plug)

本次范围为 PaperDIY 原生虚拟设备的一张会话介质。实时替换为第二张镜像、
实机电气、浏览器和其他板型为 `NOT RUN`。

冻结组合版在同一真实来宾验证四次 GPIO48 中断和 FAT32 数据持久化。 [冻结组合版复验](evidence/frozen-combined-summary.json)

同一冻结运行时也复验了原版 Cardputer ADV MP3 Player 1.0.0。来宾读到 TEST.MP3，按 Confirm 后显示播放进度，SPI CMD17 从 4 次增至 66 次，I2S PCM 捕获到 524 Hz。 [共享 SPI SD 回归](evidence/cardputer-adv-mp3-regression-summary.json)

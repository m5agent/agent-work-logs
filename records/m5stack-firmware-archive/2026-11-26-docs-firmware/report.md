# 验证与交付

文档版本为 `6ee4f2fb9dca1c671e475407cb709109a699cf1a`。例程使用 Arduino CLI 1.3.1、M5Stack board package 3.2.5 和 M5Unified/M5GFX 0.3.0。归档记录烧录偏移、分区布局、源码及全部原件散列。模拟器提交为 `76e8b35710d1879e073f73c4a03bd11b216fb95f`，运行文件 SHA-256 为 `05a148bee99d3fccc4ff3969296ccf547fea03f2d5f7b9f2d86391060b2b6d9a`。复测使用同一 ROM 和未经替换的原始合并镜像。

| 层级 | 结果 | 证据 |
| --- | --- | --- |
| CoreS3 esp32sim | PASS | 15/15，帧、串口和外设数据检查 |
| Cardputer-Adv esp32sim | PASS | 11/11，键盘、红外、音频与可写 SD 等 |
| CoreS3 UIFlow2 v2.5.3 | PASS | USB CDC REPL 返回 2，320×240 全红画面，USB 数据 PID 错误为 0 |
| CoreS3 Unit 旧候选配置 | PASS | QEMU-WASM Relay 和 Ultrasonic I2C 各一项候选通过。默认配置为 PARTIAL、FAIL |
| 真机 | NOT RUN | 范围为 virtual-device validation |
| 公开交付 | PARTIAL | 公开源码、索引、复测工具和生成媒体。原始 Arduino 镜像和 ELF 包含本地构建路径，整套原件保留于本地 |

使用归档 README 中的 `tools/run_all_esp32sim.sh`、`tools/run_all_adv.sh` 和 UIFlow2 命令复测。UIFlow2 通过官方 CDN 下载并校验。LFS 对象为压缩 SD 镜像，其 FAT32 文件为四张生成 PNG 和一个生成 WAV。公开索引 SHA-256 为 `5c4ce6cea6f91ee6aad9647afb6540d0e012ef9d46e733b7f15bbaf8a54338f2`。更新时保留此 commit 和测试记录，以新镜像散列记录任何重新构建或验证。

[固定版本与复测命令](https://github.com/m5agent/m5stack-firmware-archive/tree/11ea94398636e6b5b2c32673dbc585a5aee4cfaf)

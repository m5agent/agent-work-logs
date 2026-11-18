# NC1020 同字节恢复的面板窗口边界

两次使用 Cardputer K132 的原版 factory 应用和同一留存 8 MiB Flash、64 MiB FAT32 卡，在隔离的 Device Service 1.87.0 离线运行。已有面板追踪仅启用 `M5SW_SPI_WINDOW_TRACE=1`。两次均为零设备输入，恢复同一 99,384 字节存档，分别确认 407 个完整 SD 单块读取。原始 factory 应用的读回、ROM、NOR、留存介质和 QEMU 摘要已固定。[原版 Flash 与恢复条件](https://github.com/m5agent/agent-work-logs/blob/dfe3f8636f1ac6da1441366a979929adcc9f1ecc/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/report.md) · [固定 API](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service.openapi.yaml)

| 追踪同固件试验 | 恢复 | 首个心跳绘制数 | 地址窗口与画面 |
| --- | --- | --- | --- |
| A1 | 通过 | 1 | 原生内容行 0–239。三次有效帧均与无追踪通过组逐字节相同 |
| A2 | 通过 | 0 | 原生内容行 0–208。三次取帧中剩余内容行 209–239 全黑 |

A2 的 2,338 个完整 CASET/RASET 地址记录逐项等于 A1 的前 2,338 个记录。A2 最后窗口是 CASET `003400ab` 和 RASET `00f800f8`，对应第 208 行。三个取帧对照均确认到该行的 120 个内容列逐行与 A1 相同，侧栏另有 86 个像素不同。A1 的下一窗口 RASET `00f900f9` 对应第 209 行，A2 无后续新 CASET。两次的窗口追踪都从同会话 ZIP 独立重解析并匹配实际帧。[完整窗口、帧和存储摘要](evidence/window-only.summary.json)

这两轮保留了部分绘制，但没有重新得到无追踪的只显示第 0 行。当前样本无法确定追踪是否影响停顿位置。地址窗口及已显示颜色无法区分 SPI 传输完成、IRQ 递送、DMA 回收、驱动等待或下一行未提交。后续可使用短窗 SPI2 观察来验证已画行的完成回执和下一次来宾提交。真机、浏览器、常驻切换和 Burner 为 `NOT RUN`。[既有第 0 行证据](https://github.com/m5agent/agent-work-logs/blob/dfe3f8636f1ac6da1441366a979929adcc9f1ecc/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/evidence/row0-boundary/README.md)

# Cardputer ADV 裸板接线与 SPI SD 修复复验

- 日期为 2026-11-09，结果为 `PARTIAL`。原生虚拟设备验证通过，其他执行范围见下文。
- 工作类型为代码修复与虚拟设备验证。
- 问题来自公开版 MP3 Player 的启动黑屏和挂卡失败。[原始复核](https://github.com/m5agent/agent-work-logs/blob/0a4969c549561efcf5423a592ca567a86d838e0b/records/firmware-review-service/2026-11-09-cardputer-adv-mp3-startup/report.md)
- ESP Emulator 源码版本为 `340d80cf2e54bbe867f5dbade422ac0907251607`，基线为 `80d1879a014a55bc598fbc1474445c1f6773ff34`。
- 验证环境为 Cardputer ADV 原生 QEMU 与 Device Service。UIFlow2 使用仓库内固定回归用例。

## 结论

默认 Cardputer ADV 按裸板启动，选装的 Cap CC1101 在会话配置中显式挂载。SPI SD 模型按卡的空闲和就绪状态返回响应，并在启用后执行 CRC 校验。同一份未修改的公开固件在无卡时显示缺卡提示，在有卡时经真实模拟 SPI 路径挂载 FAT32。按回车后，同一来宾读取曲目数据并输出与合成 MP3 频率匹配的虚拟 I²S PCM。

## 关键证据

- 原生运行时 SHA-256 为 `d150c645291e66202d73eb6bdc98900980c2dcb4e851b41d9386dfa6a1ae4b7d`。
- 有卡播放会话观察到文件扇区读取和 108,032 字节的 PCM。此前的 OCR 失败与同帧 SHA 保留在独立会话记录中。
- 三款机型的 SPI SD 扇区读写和画面检查通过 12/12。Cardputer ADV 的裸板键盘、音频以及选装 Cap NFC、CC1101 四项虚拟回归通过 15/15。

## 文件

- [完整报告](report.md)
- [结构化结果](run.json)
- [脱敏执行摘要](evidence/execution-summary.redacted.json)

## 未覆盖项

Cardputer ADV 真机、SD 电气时序、音频输出品质、无线射频与声学验证为 `NOT RUN`。浏览器 WASM 见报告的独立执行结果。

浏览器独立验证覆盖同一原版固件无卡出画、Stop 清理和固定键盘回归。
[浏览器摘要](evidence/browser-summary.redacted.json) · [QEMU 补丁](patches/)

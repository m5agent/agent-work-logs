# Cardputer ADV、Dial、NC1020 与 StickS3 原生复验

- 日期 `2026-11-18`
- 结果 `PARTIAL`，限定本文列出的原生虚拟设备路径
- 工作类型 `report`，在联合验收之后继续验证原版固件或配对探针
- 源码基线 `m5stack-esp-emulator@bd1dca3c74f8b9c2654e1ba3590e1f282d2071b0`
- 独立 Device Service 会话，逐项绑定各自的源码、QEMU、固件与证据包哈希

Cardputer ADV #234 的容量冲突已在基线来宾和候选准入两处重现，官方 8 MiB 固件正控通过。独立候选解码了 Cardputer ADV 的 CRC32 和 SHA256 两种 S3 崩溃任务；K132 屏幕候选让 NC1020 同原版的完整合成画面逐像素匹配。整合版的两次无追踪运行仍有不完整 LCD 写入，稳定出帧保持 `PARTIAL`。StickS3 用同一份配置后 Flash 在新的会话验证直接以 STA 加入。Dial 的快速旋转偶发漏采样仍为 `PARTIAL`。

[原联合记录](https://github.com/m5agent/agent-work-logs/tree/6d6db56049cb29fed03b83c0577650575b8559fa/records/esp-emulator/2026-11-18-native-integrated-guest-validation) · [详细报告](report.md) · [结构化结果](run.json) · [证据索引](evidence/README.md)

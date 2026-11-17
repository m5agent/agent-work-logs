# 虚拟设备复验摘要

- [Cardputer ADV #234 容量、审核与官方正控](cardputer-adv-flash-capacity-summary.json)
- [Dial 冻结构建三轮回放](dial-frozen-replay-summary.json)、[诊断时间线](dial-diagnostic-timeline-summary.json)、[无 USB 捕获对照](dial-gpio-only-summary.json)、[包完整性与检查](dial-run-integrity-summary.json)
- [Cardputer ADV S3 CRC32 和 SHA256 任务解码](s3-coredump-summary.redacted.json)
- [NC1020 虚拟屏幕与 K132 对照](nc1020-native-geometry-summary.redacted.json)
- [StickS3 一致配置后 Flash 新会话](sticks3-new-lease-summary.redacted.json)

归档过程复核 26 个 ZIP 的 SHA-256、CRC 和清单文件逐项长度与 SHA-256，同时重算 StickS3 交换 pcap 和传递 Flash 的 SHA-256。JSON 是原始运行结果的脱敏摘要。原始二进制、设备标识、访问凭据、地址和运行路径保留在私有证据。

[整合复验](../report.md#最终整合复验)附有 Flash 拒绝、StickS3 独立抓包、S3 崩溃以及 NC1020 无追踪和追踪两组摘要。

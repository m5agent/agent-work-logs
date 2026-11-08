# StickS3 UIFlow2 TLS 时间校验复核

- 日期为 2026-11-08。
- 结果为 `PARTIAL`。指定 v2.5.5 preview 的三组时间行为通过，原 v2.5.3 和 AWS IoT 尚未复测。
- 工作类型为 issue validation。
- 问题来源为 [UIFlow #120](https://github.com/m5stack/uiflow-micropython/issues/120)。
- 源码版本为 `m5agent/m5stack-esp-emulator@dd2eb35d2e6a909992268089ddc37e27970d4a92`。
- 环境为独立 Device Service 的 StickS3 虚拟设备、受控双向 TLS peer 和实际 DeepSeek 测试执行。

## 结论

官方公开 v2.5.5 preview 应用在正确的 2026 年 RTC 下完成两个独立 TLS/HTTP 交换。2010 年和 2040 年分别得到证书尚未生效和过期的预期拒绝，两个 API 均维持 `CERT_REQUIRED`。

## 关键证据

- 官方 CDN 完整下载与缓存 base SHA 一致，应用分区及 VFS 外字节逐字节一致。
- 实际运行时绑定、串口时钟、peer 认证、证据 ZIP 和停止后历史组成同会话证据。
- 首轮串口观测配置错误保留为原始 FAIL，纠正使用 UART dupterm 后获得完整观测。

## 文件

- [完整报告](report.md)
- [结构化执行](run.json)
- [脱敏证据摘要](evidence/tls-validity-summary.json)
- [独立验收摘要](evidence/independent-audit-summary.json)

## 未覆盖项

原 v2.5.3、AWS IoT 专属账号/MQTT 和物理 Wi-Fi 均为 `NOT RUN`。本轮源码改动为零，issue 仍开放。

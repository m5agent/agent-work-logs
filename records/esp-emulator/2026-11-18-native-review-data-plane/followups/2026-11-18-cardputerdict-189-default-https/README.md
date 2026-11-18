# CardputerDict 原版默认 HTTPS 发音与音频回读

- 日期 2026-11-18，UTC+08:00
- 结果 PASS，范围为隔离 Linux 原生虚拟设备复验
- 固件 CardputerDict 0.6.4，Cardputer K132
- 环境 Device Service 1.89.0、原生 QEMU Wi-Fi、受控 DNS 和命名空间
- [合并后的源码和接口](https://github.com/m5agent/m5stack-esp-emulator/blob/1319222e0b7439789e35fd177d50b9f0371e3f11/docs/device-service-api.md)

## 结论

发布版本的隔离放行组完成 SNTP、TLS、MP3 缓存和默认 I2S 输出。普通 API、证据 ZIP 和停机后的 API 回读均核对为同一会话逐步追加的 PCM。拒绝组保留 DNS 和校时能力，发音连接无响应且没有缓存或 PCM。

## 证据

[完整报告](report.md) · [运行清单](run.json) · [两项结构化回执](evidence/README.md)

## 未覆盖项

Reviewer 保存快照、Cardputer ADV 原版联网、浏览器、真机和 Burner 均为 NOT RUN。

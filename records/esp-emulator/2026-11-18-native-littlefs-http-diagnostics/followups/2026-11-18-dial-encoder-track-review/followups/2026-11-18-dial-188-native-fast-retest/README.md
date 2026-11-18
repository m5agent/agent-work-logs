# Dial R1F30 在 Device Service 1.88 的原版快转复验

- 日期 2026-11-18，UTC+08:00
- 结果 PARTIAL，工作类型为原版固件复验
- 固件 vinylM5Dial 1.0 R1F30，8 MiB
- 环境 Device Service 1.88.0，Dial 原生 QEMU，离线虚拟设备验证
- [固定源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service-api.md)

## 结论

原版 vinylM5Dial 1.0 R1F30 借助同一虚拟 Dial 配置 和 AudioPlayer 夹具复跑两次。35 ms 档 18/18 实际选曲匹配，显式 5 ms 档 14/18 匹配。36 个输入都完成四倍边沿计数。保留 5 ms 应用行为为 `PARTIAL`。[先前复核](https://github.com/m5agent/agent-work-logs/blob/dfe3f8636f1ac6da1441366a979929adcc9f1ecc/records/esp-emulator/2026-11-18-native-littlefs-http-diagnostics/followups/2026-11-18-dial-encoder-track-review/report.md)

## 证据

[完整报告](report.md) · [运行清单](run.json) · [同会话记录](evidence/dial-r1f30-native-188.summary.json)

## 未覆盖项

实体旋钮、浏览器、实际扬声器和 Burner 均为 NOT RUN。

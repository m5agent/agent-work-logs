# CardputerDict 原版外部发音的放行和拒绝对照

- 日期 2026-11-18，UTC+08:00
- 结果 PARTIAL，工作类型为原版固件候选验证
- 固件 CardputerDict 0.6.4，Cardputer K132
- 环境 Linux 原生 QEMU、隔离 Device Service 候选、虚拟设备验证
- 本地保留候选提交 97ae097ddf1337c327e8bdbeae29642401ed5a74
- [发布基线源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service-api.md)

## 结论

放行会话观察到 SNTP、TLS、SD 缓存与诊断 I2S DMA 的非零 PCM。拒绝会话的 SNTP 和原发音域名解析仍成功，TCP 443 有两次来宾 SYN 且无响应，未生成缓存。默认音频路径和常驻审核仍待验证。

## 证据

[完整报告](report.md) · [运行清单](run.json) · [同会话摘要](evidence/cardputerdict-https-allow-deny.summary.json)

## 未覆盖项

默认音频路径、浏览器、真机响声、常驻部署、Firmware Reviewer 和 Burner 均为 NOT RUN。

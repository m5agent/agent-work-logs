# CardputerDict ADV 0.5.0 原版 HTTPS 数字发音

- 日期为 2026-11-18。工作类型为原版固件功能复验。
- 结果为 PASS，范围为隔离 Device Service 同会话的联网、缓存和默认数字音频。
- 来源为 [CardputerDict ADV 0.5.0 原版查词](../../README.md)的后续验证。
- 环境为 Linux arm64、Device Service 1.89.0、原生 Xtensa QEMU 和原版 Cardputer ADV 0.5.0，验证类型为 virtual-device validation。源码与运行时精确身份见回执。

原版通过 Fn+W 完成联网设置，查到 hello 后用 Fn+P 触发发音。证据绑定同一会话的 DHCP、受控 DNS、SNTP、HTTPS、缓存 MP3 与默认 I²S PCM。结果为一轮完整通过，另保留两次设置失败。

[完整报告](report.md) · [执行清单](run.json) · [结构化回执](evidence/adv050-https-audio-summary.json)

Reviewer 的 ADV 类型入口、实机声音、射频、浏览器和联网注册均未执行，未提交 Burner。

# Tab5 USB Host 能力常驻切换回读

- 日期：`2026-11-19`
- 结果：`PASS`，限常驻 Device Service 切换、能力与历史读回。
- 类型：`infra_baseline`
- 源码和接口：[Device Service 597e032](https://github.com/m5agent/m5stack-esp-emulator/tree/597e03214dc5f442787cec52f1720567e4ed2a00)，OpenAPI 1.99.0；Reviewer `f0101b6`。

工作台与审核执行端均已切换到同一 Device Service 源码，两套服务均报告
Tab5 USB Host 为 `partial`，均未公布 USB 端点夹具。原生 Xtensa、C6 运行时和
浏览器清单保持原哈希。

切换前后，工作台保留 55 条会话，审核执行端保留 94 条会话，Reviewer 保留 129 条
审核记录。Reviewer 代码、历史和抽查的证据 ZIP 一致，连接审核执行端后返回就绪。
没有提交 Burner。

相同实现此前实际运行了原版 Maker Fighter 1.4，确认了 USB Host 初始化和事件等待。
外设接入、枚举、端点传输、完整应用画面和真机仍待验证。
[同原版能力验证](https://github.com/m5agent/agent-work-logs/blob/cb240b4d96bfa470ff7aa19926c8c9f74931a418/records/esp-emulator/2026-11-14-p4-v1-originals/followups/2026-11-18-maker-fighter-dwc-self-check/followups/2026-11-18-maker-fighter-host-setup/followups/2026-11-18-tab5-226-usb-host-capability/README.md)

- [回读报告](report.md)
- [运行记录](run.json)
- [脱敏证据摘要](evidence/resident-readback.summary.json)

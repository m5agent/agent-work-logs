# AtomS3 原生 QEMU 常驻切换回读

- 日期 2026-11-19
- 结果 `PASS / LIVE_VERIFIED`，范围为常驻运行时与 API 回读。
- 工作类型 运行时发布验收。
- 问题来源 [AtomS3 原生显示问题 #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)，已关闭并标记完成。
- 源码版本 [`c25fdfc9623cdd716a395b881466c426b319474d`](https://github.com/m5agent/m5stack-esp-emulator/commit/c25fdfc9623cdd716a395b881466c426b319474d)。
- 环境 macOS 原生工作台与审核设备服务，Reviewer 0.29.0。

## 结果

两套 Device Service 已加载经过[独立原版固件验证](../../README.md)的签名 Xtensa QEMU，两边 OpenAPI 均返回 HTTP 200，仍是相同字节的 1.99.2。工作台保留 55 条会话，审核设备服务保留 98 条，Reviewer 保留 130 个历史任务和抽查的证据，Darwin 后端就绪。

发布回读核验了两套角色指向同一签名候选、API 和历史保留。C6、浏览器运行时、Tab5 P4 主运行时及外设部件哈希一致。切换期间未运行生产固件访客，Burner 未提交。

[发布回读报告](report.md) · [运行记录](run.json) · [脱敏证据摘要](evidence/atoms3-native-resident.summary.json)

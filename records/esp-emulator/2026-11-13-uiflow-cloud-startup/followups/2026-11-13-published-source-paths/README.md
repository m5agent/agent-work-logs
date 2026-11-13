# 已发布源码的原版配对与编程复测

- 日期：`2026-11-13`（Asia/Shanghai）。
- 结果：`PASS`，限定于下列原版镜像、原生运行时及用户路径。
- 源码：[main @ 8598b1f603ae6638a3f6d27824431781429b9e49](https://github.com/m5agent/m5stack-esp-emulator/tree/8598b1f603ae6638a3f6d27824431781429b9e49)。
- 验证方式：virtual-device validation；实际浏览器控制原生 guest，不是 browser-WASM 联网。
- 背景：源码交付和完整检查完成后，重新执行官方配对入口并保留本地编程对照。

`main` 角色完成 CoreS3/StickS3 的实际网页入口，以及 Core2、AtomS3R、StopWatch、
Cardputer ADV 的 API 入口；`review` 角色完成 CoreS3/Core2 API 入口。
八次都取得真实六位云端回复，并由执行者逐帧确认官方 Access Code 画面。
本地编程对照产生实际串口 marker 与蓝底 `Local code OK` 画面。

全部复测会话先取 evidence，再停止并释放 lease；原有历史保留。
首次 `review` CoreS3 的观察脚本路径解析失败单独保留：guest 已收到码，
手工 evidence 在运行中保存，修正观察脚本后另起会话复测通过。

- [report.md](report.md)：验收、首次观察失败、清理与边界。
- [run.json](run.json)：结构化 follow-up。
- [validation-summary.json](evidence/validation-summary.json)：脱敏白名单证据。
- [原始记录](../../README.md)：保留旧入口、未补齐镜像及早期源码检查失败。
- `patches/`、`code/`：不适用；本次为已发布源码的复测，未新增产品补丁。

未提交 Burner。物理硬件、RF、电气、功耗、声学、browser-WASM 公网与长期稳定性
未验证。服务拓扑、端点、路径、设备身份、连接凭据与配对值不公开。

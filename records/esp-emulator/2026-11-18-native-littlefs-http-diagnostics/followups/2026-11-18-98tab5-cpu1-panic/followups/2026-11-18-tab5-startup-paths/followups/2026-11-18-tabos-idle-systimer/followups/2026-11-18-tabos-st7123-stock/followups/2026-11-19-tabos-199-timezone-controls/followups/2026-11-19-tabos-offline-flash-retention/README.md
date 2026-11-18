# Tab5 原版离线向导和 Flash 持久化

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PASS`，原版离线设置经 HTTP reset 和停机保留均可读回
- 工作类型 `code_change`
- 环境 macOS ARM64，原生 `esp-emu 1.1.0`，ST7123，Device Service 1.99.1

未修改的 M5TabOS 0.9.1 在原版离线向导选择 `UTC-2:30` 和 `Não usar a internet` 后进入正常桌面。Device Service 1.99.0 的同会话复位让欢迎向导重新出现，24 KiB NVS 与原始镜像逐字节一致。候选 `76e734f5` 的真实 Device Service 1.99.1 复位后直接进入桌面，重新打开设置仍显示 `UTC-2:30`，Wi-Fi 和网络 Mesh 仍关闭。

同一个候选会话再在原版设置页改为 `UTC-2:00`。正常停机保留的完整 Flash 由 `/flash?format=bin` 读回，NVS 同一个带符号字段、页和条目 CRC 均重新核对，来宾应用区逐字节保持一致。三阶段未改动上传原件、规范化工件、运行时或 C6 镜像。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏后的帧、协议和 NVS 摘要](evidence/m5tabos-flash-retention-summary.json)

未连接网络，未上传新的原始工件或匹配 ELF。真机、浏览器、联网向导和其他固件未执行。Burner 未提交。

[前次原版时区与向导按钮验证](../../README.md)

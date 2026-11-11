# Firmware Review Service 固件运行观察与 Cardputer ADV 复审

- 日期 `2026-11-11`
- 结果 `PARTIAL`
- 工作类型 `code_change`、`service_debug`
- 问题来源为 LukewarmCard ADV (Keypad edition) 1.0 的按键功能复审。
- 源码版本和 QEMU 构建哈希见 [run.json](run.json) 与 [虚拟设备取证摘要](evidence/virtual-device-summary.json)。
- 环境为 Cardputer ADV 原生 QEMU、Device Service 与保存快照 dry-run。

原审核按了 A/B，更新后依固件说明测试 Enter 和方向键，并持续采集同一会话的状态、串口与画面至少 60 秒。LukewarmCard 在原审核后端及独立的原生 QEMU 构建中均停留在启动标志。按键输入得到接收确认，应用菜单及按键功能未取得验证证据。

- [复测过程、结果与回滚](report.md)
- [结构化运行记录](run.json)
- [取证摘要](evidence/virtual-device-summary.json)
- [审核服务补丁](patches/0001-virtual-observation.patch)

本次未运行真机、实际 M5Launcher 安装流程或浏览器后端，未提交 Burner。

# ESP Emulator 原生崩溃证据与三份原版复审

- 日期 `2026-11-17`
- 结果 `PARTIAL`
- 工作类型 `code_change`
- 问题来源 固件审核中的看门狗、重复复位和截图证据缺口
- 源码版本 Device Service `271524908363e8666148a7b60932fcaf01b5d5ff`、审核服务 `2b88a86921e01c200be1d75f98e1a146ceef7da4`
- 环境 隔离 Device Service，Core2 / StickS3 原生 QEMU，Tab5 esp-emu 0.50.0。验收层级为 virtual-device validation。

## 结论

Core2 受控 abort 与 CPU1 中断看门狗都产生同会话诊断，已匹配的 ELF 能解析受控函数，交叉 ELF 被拒绝，服务重启后仍可读取已停止会话的诊断。三份原版均得到绑定固件与会话的诊断记录，应用问题仍保留各自的复审结论。

## 关键证据

- [Core2 受控证据](evidence/core2-controlled-crash-summary.json)记录两种故障、精确 ELF 对照和重启后取证。
- [原版复审摘要](evidence/saved-original-replay-summary.json)记录 All day watch、M5TabOS 和 98TAB5 的实际结果。
- [归档完整性摘要](evidence/archive-integrity-summary.json)记录六份原始 ZIP 与被解析串口字节范围的哈希核验。

## 文件

- [报告](report.md)
- [结构化记录](run.json)
- [脱敏证据](evidence/)

测试工程随 ESP Emulator 源码维护。本记录未携带补丁或固件二进制。

## 未覆盖项

三份原版缺少匹配 ELF。All day watch 的历史看门狗原因仍未定位，M5TabOS 的非法指令与复位归因仍未确定，98TAB5 的画面与触摸待补测。物理硬件、浏览器和生产切换均为 `NOT RUN`，未提交 Burner。

## 后续验证

- [Tab5 CarPlay v1.0.0 原版 DSI 就绪](followups/2026-11-17-tab5-carplay-native-dsi/)

[离线 FreeRTOS core dump 解码](followups/2026-11-17-offline-freertos-core-dump/)保留已匹配 ELF 的任务和调用栈验证。

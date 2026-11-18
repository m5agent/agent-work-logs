# 98TAB5 原版 CPU1 异常与板级对照

- 日期 `2026-11-18`
- 整体结果 `PARTIAL`，工作类型 `service_debug`
- 对象为 98TAB5 1.3.0 原版的启动和显示，来源见[原版启动记录](../../README.md)
- 源码 [Device Service `13df3b8a7ab197df14f57d2ca8bc58919a7eb666`](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666)
- 环境为隔离的原生 Device Service、ESP32-P4 与 ESP-Hosted C6，`esp-emu 1.1.0`

## 结论

两组自然启动分别使用 GT911 Part 和内置识别寄存器，均在 35 秒内出现 18 次软件复位，均未获得完整 DSI 帧。复位在无 GT911 Part 的配置中同样复现。[板级对照摘要](evidence/98tab5-gt-board-route-comparison.summary.json)

三轮只读调试均在转储入口读到 CPU1 的指令访问异常，异常 PC 为 `0x0`。第三轮在同一启动轮次先读到 ROM 实际交接 `0x4ff00330`，随后捕获相同异常。转储写入失败发生在异常之后。[异常入口摘要](evidence/98tab5-panic-entry.summary.json)

## 文件

- [复现与分析报告](report.md)
- [结构化记录](run.json)
- [自然启动和转储序列](evidence/98tab5-gt-board-route-comparison.summary.json)
- [只读断点观察](evidence/98tab5-panic-entry.summary.json)

## 未覆盖项

ROM 交接后绕转到 `0x0` 的具体路径、固件与运行时各自责任和原版完整显示仍待定位。真机、browser-WASM 及外部网络为 `NOT RUN`，未提交 Burner。

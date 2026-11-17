# Tab5 ST7123 并发 DSI 取帧复验

- 日期 2026-11-17
- 结果 `PARTIAL`，虚拟设备验证
- 工作类型 `code_change`
- 问题来源 关机并发复验中，虚拟 P4 EN 拉低后缺少原版关机帧
- 源码版本 `ddb6027e695f82bdc593b80599af73925b88ed5d`

使用同一份未改动的 Arduventure 1.0.0 BIN 验证。四个无缓存 PNG 客户端按 125 ms 节奏请求时，基线和候选均取得原版关机帧、EN 低电平、证据 ZIP 与显式重启后的标题帧。候选该次复验返回 237 张图，基线 96 张。25 ms 对照中，候选一次全流程通过，另一次重启标题帧超时。通过的高压样本仍有原生 TCP 广播丢弃警告。

- [报告](report.md)
- [结构化记录](run.json)
- [脱敏证据](evidence/dsi-receiver-summary.json)
- [原版关机复现脚本](https://github.com/m5agent/m5stack-esp-emulator/blob/ddb6027e695f82bdc593b80599af73925b88ed5d/tests/firmware/tab5_st7123/run_power.py)

冻结组合版验证原版关机帧、EN 和重启。 [冻结组合版复验](evidence/frozen-combined-summary.json)

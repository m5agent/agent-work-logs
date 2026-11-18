# 98TAB5 原版 CPU1 启动跳转定位

- 日期 `2026-11-18`
- 整体结果 `PARTIAL`，工作类型 `service_debug`
- 来源 [原版 CPU1 异常与板级对照](../../README.md)
- 执行源码 [Device Service `13df3b8a7ab197df14f57d2ca8bc58919a7eb666`](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666)
- 环境为隔离的原生 Device Service、esp-emu 1.1.0、GT911 内置识别寄存器

两轮只读调试都观察到 CPU1 从 DROM 地址 `0x4015cc58` 读到零，随后的实际间接跳转目标为 `0x0`，触发指令访问异常。两种 Flash 文件在对应偏移 `0x3cc58` 的同一项均为 `0x4ff00cca`。运行中该地址为何读零仍待定位。[同一原版验证摘要](evidence/98tab5-startup-dispatch.summary.json)

- [报告与复现](report.md)
- [结构化记录](run.json)
- [有界证据](evidence/98tab5-startup-dispatch.summary.json)

两轮均无完整 DSI 帧。真机、浏览器及外部网络均未执行。未提交 Burner。

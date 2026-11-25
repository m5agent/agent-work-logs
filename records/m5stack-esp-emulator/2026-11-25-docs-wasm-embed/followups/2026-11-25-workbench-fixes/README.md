# 文档预览隔离提示和 CoreS3 M5UI 调度修复

- 日期 `2026-11-25`
- 结果 `PASS`（本地浏览器隔离提示和限定 M5UI 回归），`PARTIAL`（正式文档嵌入和完整复用）
- 工作类型 `code_change`
- 来源 [文档 iframe 问题 #242](https://github.com/m5agent/m5stack-esp-emulator/issues/242) · [官方 M5UI Button](https://uiflow-micropython.readthedocs.io/en/latest/m5ui/button.html)
- 源码 [m5stack-esp-emulator @ afd1c635fa702b201508a5d5d689cb67ed1243f3](https://github.com/m5agent/m5stack-esp-emulator/tree/afd1c635fa702b201508a5d5d689cb67ed1243f3) 的浏览器候选改动
- 环境 Chrome 158.0.8127.37、macOS、本地静态导出、浏览器 WASM 虚拟设备验证

隔离失败后执行面板保留失败原因和新标签页打开提示。CoreS3 默认浏览器 MicroPython 编程镜像应用了既有 M5UI 调度合并机制。独立按钮验证及六个官方例程连续执行通过。同源隔离文档预览的两款设备各两次正常退出。

- [修复和证据说明](report.md)
- [结构化记录](run.json)
- [隔离与启动实测](evidence/iframe-summary.json)
- [M5UI 原始对照与候选证据](evidence/uiflow-lvgl-summary.json)

[合并后的浏览器回归](evidence/combined-regression-summary.json)包括 iframe 条件与两款机型的完整或快速编辑器验收。

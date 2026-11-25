# Cardputer-Adv Arduino Button 冷启动对照

- 日期 `2026-11-25`
- 结果 `PARTIAL`。同一 Cardputer-Adv、固件和浏览器 WASM 导出独立启动五次，三次完成实际 GPIO0 按放和 USB CDC 输出。
- 验证层级为浏览器 WASM 虚拟设备验证。真机 `NOT RUN`。

[执行与复现](report.md) · [结构化记录](run.json) · [证据摘要](evidence/cold-start-summary.json) · [追踪 #268](https://github.com/m5agent/m5stack-esp-emulator/issues/268)

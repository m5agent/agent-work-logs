# ESP Emulator Issue 复验与修复

- 日期 `2026-11-09`
- 结果 `PARTIAL`。Classic 烧录、StickS3 审查判定和完整 Flash 重放完成同路径复验。Tab5、全矩阵并发门禁和帧方向提示仍开放。
- 工作类型 `issue`
- 源码 `m5agent/m5stack-esp-emulator` @ `4b1dbc8bea1b79a7e1cf5ce3e26a67a3c0982e61`
- 环境 macOS arm64，原生 QEMU、隔离 Device Service 和独立 esp-emu

[复验报告](report.md) · [结构化记录](run.json)

- [Classic 串口烧录 33 次对照](evidence/classic-uart-summary.json)
- [Canonical 118 Atom Lite 交叉复验](evidence/classic-uart-canonical118-summary.json)
- [StickS3 按键和就绪判据](evidence/sticks3-input-and-readiness-summary.json)
- [五个原样本的具名缺口](evidence/sticks3-gap-summary.json)
- [完整 Flash 跨会话重放](evidence/flash-replay-summary.json)
- [Tab5 稳定版与预发布版](evidence/tab5-188-summary.json)
- [高负载基线帧复核](evidence/peripheral-192-summary.json)

真机、物理无线和本次浏览器部署均 `NOT RUN`。公开记录仅含受限摘要、哈希与必要标记。

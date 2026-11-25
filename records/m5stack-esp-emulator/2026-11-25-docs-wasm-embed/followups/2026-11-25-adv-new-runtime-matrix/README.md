# Cardputer-Adv 新 WASM 同固件回归

- 日期 `2026-11-25`
- 结果 `PARTIAL`
- 工作类型 `report`
- 来源 [Cardputer Arduino 例程](https://docs.m5stack.com/en/arduino/m5cardputer/program)
- 源码 [板型探测修复 PR #256](https://github.com/m5agent/m5stack-esp-emulator/pull/256)
- 环境 Chrome 158.0.8127.37、macOS，浏览器 WASM 虚拟设备验证

新 WASM 验证了直达 Display、Keyboard 和 Quick Start 图形动画。补跑原外设例程后，电池、IMU、麦克风可见初始应用画面。USB CDC 对照与卡片资料用更具体的输入方案分别取证。

- [新运行时回归与问题边界](report.md)
- [结构化执行记录](run.json)
- [同会话固件、原始帧、串口和清理](evidence/adv-browser-followup-summary.json)

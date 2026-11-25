# 原 Arduino 例程的机型探测与 CoreS3 Unit 连接

- 日期 `2026-11-25`
- 结果 `FAIL`（Cardputer-Adv 显示及键盘例程；CoreS3 Ultrasonic-I2C），`PARTIAL`（CoreS3 Relay）
- 工作类型 `report`
- 来源 [Cardputer Arduino](https://docs.m5stack.com/en/arduino/m5cardputer/program) · [CoreS3 Arduino](https://docs.m5stack.com/en/arduino/m5cores3/program)
- 源码 [m5stack-esp-emulator @ afd1c635fa702b201508a5d5d689cb67ed1243f3](https://github.com/m5agent/m5stack-esp-emulator/tree/afd1c635fa702b201508a5d5d689cb67ed1243f3)
- 环境 Chrome 158.0.8127.37，macOS，工作台静态导出，浏览器 WASM 虚拟设备验证

ADV 显示例程识别成 StampS3，随后除零重启。键盘例程接受 QEMU 输入但没有终端画面。CoreS3 的 Ultrasonic-I2C 例程因 I2C NACK 持续显示失败回退值。Relay 能切换界面状态，虚拟继电器输出未验收。

- [复现和验收](report.md)
- [结构化记录](run.json)
- [脱敏来宾摘要](evidence/board-probe-and-unit-summary.json)

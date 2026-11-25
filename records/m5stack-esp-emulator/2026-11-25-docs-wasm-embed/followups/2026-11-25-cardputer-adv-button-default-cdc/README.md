# Cardputer-Adv 默认 CDC 的 Button 原例程复验

- 日期 2026-11-25
- 类型 bug-fix follow-up，virtual-device validation
- 设备 Cardputer-Adv，浏览器 WASM
- 问题 [默认 USB CDC Button #257](https://github.com/m5agent/m5stack-esp-emulator/issues/257)

合入 USB 控制器后，锁定工作台上的同一默认 Arduino 原固件进行三次独立正常执行。每次真实 G0 按放产生两条 USB 应用信息，控制器都新增 37 字节与 8 个包。独立的同 WASM 跟踪确认实际来宾 GPIO 输入寄存器读出高、低、高。保留早期无应用报文与 `ipc1` 启动异常的记录。

- [复现与范围](report.md)
- [结构化执行记录](run.json)
- [输入、实际 CDC 控制器和 Worker 回收](evidence/button-reruns.summary.json)

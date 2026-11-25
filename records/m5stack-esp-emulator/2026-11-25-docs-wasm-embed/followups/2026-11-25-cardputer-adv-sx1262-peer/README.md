# Cardputer-Adv LoRa1262 与 LoRa868 原例程的 SX1262 双来宾验证

- 日期 2026-11-25
- 类型 fix preview，virtual-device validation
- 设备 Cardputer-Adv，Chromium 156.0.8078.4
- 问题 [模拟器 #244](https://github.com/m5agent/m5stack-esp-emulator/issues/244)

两款 Cap 分别使用自己的原始 UIFlow2 发端和收端。发端通过实际浏览器键盘输入 `wasm` 并按回车。SX1262 模型发端 FIFO、收端 DIO1 和 SPI 读取与原 LCD 的 `wasm` 输出一致。两组都在私有候选验证并回收 Worker。

- [实际接线、控制器与范围](report.md)
- [结构化记录](run.json)
- [实际 FIFO、输入、帧和清理](evidence/lora-pair.summary.json)
- [候选补丁及复现步骤](code/)

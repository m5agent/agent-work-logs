# Nesso N1 原版 RFID UART1 收包与复位对照

- 日期为 2026-11-18。工作类型为 issue 复验。
- 结果为 PARTIAL。UART1 收包与错误分支对照通过，原版持续运行失败，读卡未验。
- 来源为 [#216](https://github.com/m5agent/m5stack-esp-emulator/issues/216)。本轮跟进[原版看门狗和横屏复验](../../README.md)。
- 环境为隔离 Device Service 1.89.0、原生 ESP32-C6 QEMU 和 Nesso N1 原版 2.7.21，验证类型为 virtual-device validation。固定源码和运行时身份见回执。

四轮冷启动使用同一原版。正确帧通过 UART1 交给原版驱动，等待超时由四次降至零。只损坏数据校验字节时，来宾记录四次数据校验错误。四轮各发生一次软件复位。原版把帧尾字节当作数据打印的现象也有具体报文可复核。

[完整报告](report.md) · [验证清单](run.json) · [结构化回执](evidence/nesso-rfid-uart1-summary.json) · [UART1 诊断对端](code/uart1_peer.py)

实机 PN532Killer 数据、实际标签读取、修订固件和 Burner 提交均未发生。

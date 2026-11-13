# StickC Plus2 上 JIGGLER 的蓝牙时钟初始化

- 日期 `2026-11-13`
- 结果 `FAIL`（原始固件虚拟启动），`REVIEW`（默认计时下看门狗的完整根因）
- 工作类型 `issue`
- 对象为 JIGGLER 1.0、StickC Plus2 与经典 ESP32 QEMU 模型。

同一 BIN 在两次自动计时对照中触发蓝牙低功耗时钟断言。反汇编显示原 BIN 对经典 ESP32 的两个蓝牙时钟寄存器写入后立即回读。测试版本的 DPORT 模型未处理这两个偏移，读返回零，写入未保留。默认计时下的 CPU1 中断看门狗尚未完全定位。

- [诊断和复现方法](report.md)
- [结构化运行记录](run.json)
- [脱敏串口与采样摘要](evidence/virtual-startup-summary.json)

# CoreS3 UIFlow2 原文档例程修复

- 日期 `2026-11-25`
- 结果 `PASS`（实际执行路径上的导入、发送及看门狗超时），`PARTIAL`（UART 接收、来宾看门狗重启后编辑器恢复）
- 工作类型 `code_change`
- 来源 [官方 UIFlow2 硬件例程](https://github.com/m5stack/uiflow-micropython/tree/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/hardware)
- 源码 `uiflow-micropython a61a2940…95b6` → `73696ca9…50e5`
- 环境 CoreS3 UIFlow2 v2.5.3 浏览器编程候选，Chrome 158.0.8127.37，macOS，浏览器 WASM 虚拟设备验证

修复 ADC、GPIO、WDT 的显式导入，给 UART1 发送示例提供字节输入。当前候选板级配置未提供 UART1 对端，实际 RX 未走通。WDT 执行到预期重启后，编辑器未在观察窗恢复，工作台停止可正常清理。

- [修改与复验](report.md)
- [结构化记录](run.json)
- [前后源文件、实际固件、运行时和串口证据](evidence/sdk-examples-before-after-summary.json)

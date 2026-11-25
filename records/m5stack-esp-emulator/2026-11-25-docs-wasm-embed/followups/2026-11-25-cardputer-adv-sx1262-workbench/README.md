# Cardputer-Adv LoRa1262 和 LoRa868 工作台验收

- 日期 `2026-11-25`
- 问题 [m5stack-esp-emulator #244](https://github.com/m5agent/m5stack-esp-emulator/issues/244)
- 结果 浏览器虚拟设备验证 `PASS`

两种 Cap 分别在锁定的 0046 WASM 上通过双来宾验收。工作台从已校验的官方 UIFlow2 启动镜像加载四份原例程。每次先观察收端，确认无对端时接收计数为零，再通过同源标签页配对。发端输入 `wasm` 并按 Enter，实际 SX1262 TX FIFO 提交四字节。收端 DIO1 与 RX_DONE 确实置位，原程序读取 SPI FIFO，原回调显示收到的文本。两组共四台来宾均正常退出，每组的 12 个 Worker 在上下文关闭前全部回收。

- [完整报告和复现步骤](report.md)
- [运行记录](run.json)
- [脱敏机器证据](evidence/sx1262-workbench-pairs.json)
- [标准工作台回放脚本](code/run-workbench-dual-lora-0046.mjs)

物理 RF、文档嵌入和 Pages 部署需独立验收。

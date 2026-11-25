# Cardputer-Adv CC1101 Cap 工作台双来宾验证

- 日期 `2026-11-25`
- 问题 [m5stack-esp-emulator #247](https://github.com/m5agent/m5stack-esp-emulator/issues/247)
- 结果 浏览器虚拟设备验证 `PASS`

锁定的 0045 WASM 全量构建通过。新工作台入口在两个同源标签页分别启动 CC1101 Cap 发端和收端，两端通过界面载入并执行原例程。收端无对端时四项接收计数均为零。配对后，发端实际 SPI TX FIFO 的 21 字节帧被接收模型原样接受。收端生成一次 GDO0 完成通知，原程序读出 23 个 FIFO 字节并报告 `RX=1 CRC=0`，有效载荷为 `CC1101, SEQ=0, Hello`。两端通过工作台停止后正常退出，12 个 Worker 全部回收。

- [验证详情和复现步骤](report.md)
- [运行记录](run.json)
- [脱敏机器可读证据](evidence/cc1101-workbench-pair.json)
- [实际工作台回放脚本](code/cc1101-workbench-pair.mjs)

物理 RF、NFC、文档嵌入和 Pages 部署状态待独立验证。

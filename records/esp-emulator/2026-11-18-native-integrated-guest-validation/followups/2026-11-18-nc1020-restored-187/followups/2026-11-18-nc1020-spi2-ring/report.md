# NC1020 原版 K132 SPI2 事务结束与中断路由

三个隔离会话使用同一未改的原版 factory 应用、8 MiB 留存 Flash 和 64 MiB FAT32 卡。Device Service 1.87.0 离线，来宾输入为零。使用单独构建的原生 QEMU 诊断二进制，通过 M5SW_K132_SPI2_RING 启用容量为 16,384 条的内存记录。每轮常规取三张帧，第三张之后从 /machine 的只读 QOM 属性读回一次。三个会话均恢复相同的 99,384 字节存档，各完成 407 个 SD 单块读取，正常停止并释放可变 Flash，租约归零。[固定接口](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md)

| 会话 | 恢复 | 最后一行完整内容 | 帧内非黑像素 |
| --- | --- | --- | --- |
| A1 | PASS | 22 | 1,820 |
| A2 | PASS | 63 | 5,714 |
| A3 | PASS | 239 | 25,112 |

从原始记录逐项重建各内容行。每个已画行的 GDMA 请求和读回均为 240 字节。对应面板传入 240 字节后出现 TRANS_DONE。部分画面中已经绘制的内容像素和 A3 一致，剩余内容全黑。三份 ZIP 清单、九张 PNG、三个原始环和固件及运行时身份均已独立复核。[逐次摘要](evidence/k132-spi2-ring.summary.json)

A1 完整绘制第 22 行后，下一行的 RASET 命令字节到达面板，且观察到同 A3 对应事务一致的 TRANS_DONE。记录到此结束。A3 随后出现 CPU1 的 CLEAR 和四字节 RASET 参数。A2 在第 63 行颜色传输完成后，SPI2 源 21 令 CPU0 的中断输入第 8 位置位。随后观察到该路由关闭，与 A3 同一行对应事务的顺序相同。A2 的环中没有 A3 接着出现的 CPU1 CLEAR 和下一 CASET。

中断矩阵证据只覆盖模拟中断输入及采样的路由。来宾 ISR、任务和队列状态没有观测值。环容量覆盖了所有恢复内容行，部分启动记录已被覆盖。两次部分绘制在不同阶段出现，当前结果未定位共同根因。发布构建的窗口追踪和无追踪寄存器对照分别留档。诊断构建只用于这次隔离复验，实体可见效果和浏览器均未执行。[窗口追踪](https://github.com/m5agent/agent-work-logs/blob/fc8044a17ef6f863c92e47c5a5d338a57a175429/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/followups/2026-11-18-nc1020-window-only/report.md) · [无追踪寄存器](https://github.com/m5agent/agent-work-logs/blob/fc8044a17ef6f863c92e47c5a5d338a57a175429/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/followups/2026-11-18-nc1020-trace-off-mmio/report.md)

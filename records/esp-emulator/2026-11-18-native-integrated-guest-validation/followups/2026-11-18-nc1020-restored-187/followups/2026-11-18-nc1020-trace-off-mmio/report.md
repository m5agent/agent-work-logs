# NC1020 关闭追踪时的静态寄存器采样

使用同一未改原版 factory 应用、同一 8 MiB 留存 Flash 和同一 64 MiB FAT32 卡，在冻结 Device Service 1.87.0 的 K132 Cardputer 原生 QEMU 运行两个新会话。来宾离线，输入为零。两次均复原 99,384 字节存档，对应 407 个完成的 SD 单块读取。会话 ZIP 在停止前取得，停止后释放可变 Flash，保留历史并确认租约归零。[原版 Flash 与恢复条件](https://github.com/m5agent/agent-work-logs/blob/dfe3f8636f1ac6da1441366a979929adcc9f1ecc/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/report.md)

两次关闭面板、SPI 和 DMA 追踪。按同一节奏采三张普通帧，第三张帧后才通过隔离监控连接执行两次只读物理内存及 CPU 寄存器取样。采样前以 QMP query-status 确认运行态。逐一核对 ZIP CRC、清单文件、输入镜像身份、六张实际 PNG 和四组后置采样。[固定源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md)

| 会话 | 存档恢复 | 画面 | 非黑像素 |
| --- | --- | --- | --- |
| A1 | PASS | 原生内容行 0–239 完整绘制 | 25,112 |
| A2 | PASS | 内容行 0–102 与 A1 逐字节相同，行 103–239 全黑 | 10,241 |

四次后置采样读到同样的 SPI2、SPI3 TRANS_DONE raw、enable 和 masked status，均为 0x1000。两核心对应的 SPI2 和 SPI3 中断路由均未分配。五路 GDMA 输出状态和所查中断字段逐项相同。这是截屏后的稳定读值，首个缺失行发生时的控制器完成、确认、IRQ 路由和下一行提交均需在发生时观察。[寄存器范围、原始 ZIP 与图像摘要](evidence/mmio-only.summary.json)

此前无追踪试次的部分画面停在第 0 行。本次另一组关闭追踪的试次停在第 102 行，独立的窗口追踪试次停在第 208 行。无追踪自身也存在不同停顿位置。三组小样本仍无法归因于追踪开关或确定固件与模拟器的责任。仅执行隔离诊断，虚拟会话已清理。真机、浏览器、发布和 Burner 均为 NOT RUN。

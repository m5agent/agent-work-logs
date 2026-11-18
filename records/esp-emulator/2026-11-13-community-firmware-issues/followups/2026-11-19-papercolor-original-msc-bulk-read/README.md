# PaperColor 原版厂测 USB MSC 块读取验证

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PARTIAL`。两个独立首启动会话的 `READ(10)` `PASS`，初次读取和应用稳定性仍有边界。
- 工作类型 `report`。本次延续原版厂测固件的 USB 控制传输记录。 [#220](https://github.com/m5agent/m5stack-esp-emulator/issues/220)
- 环境 macOS ARM64，Device Service 1.99.0，原生 Xtensa QEMU，PaperColor ESP32-S3 USB OTG Buffer DMA

## 结论

原版厂测固件通过实际 USB Bulk-Only Transport 处理 `INQUIRY`、`READ CAPACITY(10)` 和 `READ(10)`。两个独立会话在首启动周期分别读回 LBA 0、LBA 1，各 4,096 字节和成功的命令状态。返回内容分别与原厂镜像的 FAT 引导扇区及首份 FAT 表逐字节一致。

首次 LBA 0 也返回全部原始字节，但在取得命令状态前 USB 断开。来宾串口显示 `xTaskPriorityDisinherit` 并重启。省略 `READ(10)` 的控制组同样触发该断言。原版应用稳定性仍为 `PARTIAL`。

## 关键证据

- 各次枚举通过原版描述符、地址、配置和 `GET_MAX_LUN`。已完成的 Bulk 事务均核对 CSW 签名、回显 tag、状态和剩余字节。
- `READ CAPACITY(10)` 返回最大 LBA 1519、块长 4,096 字节。读块各有 64 个 64 字节 IN 包；两次成功状态均为 `status=0, residue=0`。
- 所有会话均保留同会话 ZIP、USB 收发顺序及串口摘要，随后释放 Flash 和租约。

## 文件

- [执行报告](report.md)
- [结构化记录](run.json)
- [脱敏后的 USB 事务和介质对照](evidence/bulk-read-summary.json)

本次没有源码补丁或常驻服务改动。USB 块写入、browser-WASM、物理 USB 和长时间运行均未执行。Burner 未提交。

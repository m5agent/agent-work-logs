# Cardputer NC1020 原版 1.1 的 G0 存档和冷启动回读

- 日期为 2026-11-19（UTC+08:00）。
- 结果为 `PARTIAL`。存档与回读 `PASS`，完整画面 `PARTIAL`，实体设备 `NOT RUN`。
- 工作类型为原版虚拟设备复测。此前定位记录为 [原版双核 SPI 锁取证](../2026-11-18-nc1020-dual-core-cas/)。
- 源码为 `m5stack-esp-emulator @ 597e03214dc5f442787cec52f1720567e4ed2a00`。
- 测试环境为 macOS 上隔离的 Device Service 1.99.0、原生 QEMU Xtensa、Cardputer K132、实际 SPI SD 卡模型。 [固定版本 API](https://github.com/m5agent/m5stack-esp-emulator/blob/597e03214dc5f442787cec52f1720567e4ed2a00/docs/device-service-api.md)

## 结论

原版镜像使用同一份已导入 ROM/NOR 的 Flash 启动。工作器 A 通过 G0 写入新的 99,384 字节存档。工作器 B 从 A 停机导出的整卡启动，来宾实际读卡并恢复该文件。六张定时取样的画面都有非黑像素，两个会话各自保持同一张不完整画面。

## 关键证据

- A 恢复时完成 407 个 CMD17 单块读取。G0 按住 0.85 秒后，串口确认保存，同一介质的写入时间戳前进，累计读计数增加至 619。
- B 从 A 导出卡开机，完成 410 个 CMD17 单块读取。停机读回的存档大小和 SHA-256 与 A 一致。
- A、B 分别记录 87、86 次应用心跳，循环计数增加，两个会话的绘制增量总和都为零。
- 两份会话 ZIP 已核对 CRC、串口及 Flash/SD 身份；两次停机都保留记录、释放可写 Flash，工作器均无活动租约。 [复测报告](report.md) · [结构化结果](run.json) · [证据摘要](evidence/nc1020-199-cold-restore.summary.json)

## 未覆盖项

实体 Cardputer、浏览器 WASM、云审查与 1.99 的指令级 SPI 锁归因均为 `NOT RUN`。本次只执行原版复测，因此没有补丁或新构建。

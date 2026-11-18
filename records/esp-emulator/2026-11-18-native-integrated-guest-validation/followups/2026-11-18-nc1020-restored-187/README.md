# NC1020 留存存档与显示对照

- 日期为 `2026-11-18`
- 结果为存储 `PASS`，显示 `PARTIAL`
- 工作类型为 `report`
- 原工作记录覆盖原版冷导入、G0 保存、跨服务恢复和 LCD 诊断。[前次 NC1020 记录](https://github.com/m5agent/agent-work-logs/blob/238021b45acdef2e6d7142c8fb0d19712833a84fa1/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-storage-display-attribution/README.md)
- 源码为 esp-emulator `d25eae8db848918e9cafebc127a53a0f989941d4`。[固定源码](https://github.com/m5agent/m5stack-esp-emulator/commit/d25eae8db848918e9cafebc127a53a0f989941d4)
- 环境为 Cardputer K132 原版 NC1020、离线原生 QEMU、独立 Device Service 1.87.0 和留存的 64 MiB FAT32 卡。

## 结果

两次都恢复了同一份 99,384 字节状态文件，独立控制器计数各有 407 个完整读块。
第一轮的三张直接采样帧完整匹配 240×135 作者图案。第二轮的三帧均只有
120 个非黑像素。两次来宾都持续发出心跳，首次心跳的周期和 RTC 相同，
绘制计数分别为 1 和 0。存储 2/2 通过，显示 1/2 通过。

## 证据

- 源码、OpenAPI、QEMU、ROM、应用、留存 Flash 和 FAT32 均记录固定哈希。
- 同一会话串口、SPI SD 读块计数、文件清单和三次帧采样绑定到证据 ZIP。
- 两轮均保留会话历史，释放 Flash 和租约，来宾与隔离服务均退出。

[执行报告](report.md) · [运行清单](run.json) · [脱敏证据](evidence/README.md)

## 验证范围

本次是留存状态恢复的 virtual-device validation。实体设备、浏览器、从空 Flash 导入、
恢复后再次保存、原版来宾的 SPI 锁现场和 Burner 均为 `NOT RUN`。

## 后续复验

[NC1020 原版双核 SPI 锁交接](followups/2026-11-18-nc1020-dual-core-cas/README.md)

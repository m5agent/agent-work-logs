# NC1020 原版 SPI2 完成和中断路由复验

- 日期 2026-11-18，UTC+08:00
- 结果 PARTIAL，工作类型为原版固件诊断复验
- 固件 NC1020，原版 factory 应用随 8 MiB Flash 恢复
- 环境 Device Service 1.87.0、K132 Cardputer 原生 QEMU 诊断构建，离线虚拟设备验证
- [固定源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md)

## 结论

三个冷会话均恢复存档。一次完整绘制，两次分别停在第 22、63 行之后。在部分画面中，已画行的 GDMA、面板传输和 TRANS_DONE 连续可见。两次停顿对应的下一来宾事务阶段不同，共同根因待定位。[前次原版恢复](https://github.com/m5agent/agent-work-logs/blob/fc8044a17ef6f863c92e47c5a5d338a57a175429/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/report.md)

## 证据

[完整报告](report.md) · [运行清单](run.json) · [同会话诊断摘要](evidence/k132-spi2-ring.summary.json)

## 未覆盖项

来宾 ISR 执行、任务阻塞、总线所有权、驱动队列状态、真机、浏览器、发布和 Burner 均为 NOT RUN。

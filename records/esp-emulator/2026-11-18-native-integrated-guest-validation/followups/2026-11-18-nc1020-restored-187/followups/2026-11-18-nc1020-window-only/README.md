# NC1020 原版恢复后的面板窗口对照

- 日期 2026-11-18，UTC+08:00
- 结果 PARTIAL，工作类型为原版固件追踪复验
- 固件 NC1020，原版 factory 应用随 8 MiB Flash 恢复
- 环境 Device Service 1.87.0，Cardputer K132 原生 QEMU，离线虚拟设备验证
- [固定源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md)

## 结论

两次原版状态恢复均通过。仅启用面板地址窗口追踪时，一次完整显示，一次停在原生内容第 208 行之后。另行保留此前无追踪的第 0 行停顿。窗口追踪是否改变停顿位置尚未定位。[前次无追踪对照](https://github.com/m5agent/agent-work-logs/blob/dfe3f8636f1ac6da1441366a979929adcc9f1ecc/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/report.md)

## 证据

[完整报告](report.md) · [运行清单](run.json) · [同会话窗口与画面](evidence/README.md)

## 未覆盖项

SPI 完成、中断投递和来宾下一行提交待定位。真机、浏览器、发布和 Burner 均为 NOT RUN。

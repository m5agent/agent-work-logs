# NC1020 关闭追踪时的后置寄存器对照

- 日期 2026-11-18，UTC+08:00
- 结果 PARTIAL，工作类型为原版固件复验
- 固件 NC1020，原版 factory 应用随 8 MiB Flash 恢复
- 环境 Device Service 1.87.0，Cardputer K132 原生 QEMU，离线虚拟设备验证
- [固定源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md)

## 结论

两次恢复均通过。一次画面完整，一次只画到原生内容第 102 行。禁用运行追踪，在正常取帧后读取寄存器，两个试次的 SPI2、SPI3、GDMA 和中断矩阵稳定读值相同。首个缺失传输与中断事件仍待定位。[前次恢复对照](https://github.com/m5agent/agent-work-logs/blob/dfe3f8636f1ac6da1441366a979929adcc9f1ecc/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/report.md)

## 证据

[完整报告](report.md) · [运行清单](run.json) · [同会话摘要](evidence/mmio-only.summary.json)

## 未覆盖项

绘制时的寄存器变化、DMA 结果回收、真机、浏览器和 Burner 均为 NOT RUN。

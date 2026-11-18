# Dial 原版快转的 GPIO、窗口和选曲时间线

- 日期 2026-11-18，UTC+08:00
- 结果 PARTIAL，工作类型为原版固件诊断复验
- 固件 vinylM5Dial 1.0 R1F30，8 MiB
- 环境 Device Service 1.88.0、原生 QEMU 诊断构建 V2，离线虚拟设备验证
- [固定源码与接口](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service-api.md)

## 结论

诊断构建两次冷启动，35 ms 选曲 18/18，5 ms 选曲 17/18。偏差的一次输入发出 64 个有序 GPIO 边沿，其中一个相位没有实际 GPIO_IN1 读取，最终 UART 选到曲目 1，预期曲目 7。LCD 操作与该相位重叠。LCD 对漏读的因果关系待定位。[无追踪对照](../2026-11-18-dial-188-native-fast-retest/report.md)

## 证据

[完整报告](report.md) · [运行清单](run.json) · [逐动作时间线摘要](evidence/dial-188-v2-correlation.summary.json)

## 未覆盖项

实体旋钮、浏览器、实际扬声器、Burner 与诊断构建的发布验收均为 NOT RUN。

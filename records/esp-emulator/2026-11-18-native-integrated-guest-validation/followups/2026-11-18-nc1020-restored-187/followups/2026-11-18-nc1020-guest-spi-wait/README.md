# NC1020 原版停顿后的来宾 SPI 等待状态

- 日期 2026-11-18，UTC+08:00
- 结果 PARTIAL，范围为原版冷复验与只读任务现场
- 固件 NC1020，Cardputer K132
- 环境 Device Service 1.87.0 原生 QEMU，零输入、离线虚拟设备
- [固定接口](https://github.com/m5agent/m5stack-esp-emulator/blob/d25eae8db848918e9cafebc127a53a0f989941d4/docs/device-service-api.md)

## 结论

四个调度采样会话均恢复存档。三次部分绘制时，LCD 任务等候空 SPI 设备信号量，结果队列已有一条完成消息，主锁保留请求位且无获取者。完整绘制对照等待正常帧队列。形成该状态的事件顺序仍待定位。

## 证据

[完整报告](report.md) · [执行清单](run.json) · [原版和来宾摘要](evidence/README.md)

## 未覆盖项

首次事务交错、根因修复、真机、浏览器和 Burner 为 NOT RUN。

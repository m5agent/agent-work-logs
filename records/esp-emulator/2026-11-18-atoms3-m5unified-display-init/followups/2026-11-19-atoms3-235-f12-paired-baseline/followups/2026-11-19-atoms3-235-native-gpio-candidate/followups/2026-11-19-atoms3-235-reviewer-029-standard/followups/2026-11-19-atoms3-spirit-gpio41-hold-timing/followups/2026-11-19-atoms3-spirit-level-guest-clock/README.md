# Spirit Level v1.0.0 来宾按键时钟复验

- 日期 2026-11-19
- 结果 `PASS`，解释了原版 600 毫秒和 2200 毫秒指令送达后的应用分支。验证类型为原生虚拟设备。
- 来源 [AtomS3 #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235) 和[前序 GPIO41 配对时序](../../README.md)。
- 环境 Device Service 1.99.3，原生 `m5atoms3-st7735`，同一 Spirit Level v1.0.0 原版与签名 QEMU。

600、610、700、2200、2350 毫秒的请求在原版应用释放分支中分别读到 588、597、690、2188、2340 毫秒。原版在按住期间保存最后一次有效采样时长。首次低样本到接纳按下有约 10 毫秒，最后低样本与第一次高样本之间另有最多 3 毫秒。五项结果帧与无观测器对照逐字节相同。较早的无观测器 610 毫秒对照曾归零，临界结果随采样时点变化。

真机、浏览器、标准 Reviewer 和其他板型未运行。未提交 Burner。

[复验报告](report.md) · [运行记录](run.json) · [证据摘要](evidence/atoms3-spirit-guest-clock.summary.json)

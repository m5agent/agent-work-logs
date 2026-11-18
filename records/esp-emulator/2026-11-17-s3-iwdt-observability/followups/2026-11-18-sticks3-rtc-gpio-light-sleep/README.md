# StickS3 RTC GPIO 浅睡唤醒

- 日期为 `2026-11-18`
- 结果为 `PARTIAL`，工作类型为原生虚拟设备验证
- 原版为 All day watch v0.3.8，另有基于 ESP-IDF 的 RTC 定时器及 GPIO 探针

旧运行时的原版长按对照出现后端 IWDT stage 0。首两份 GPIO 模型候选仍触发原版 CPU1 看门狗。第三份候选及最终运行时各用 B 键唤醒同一原版 BIN。两个 65 秒观察窗均未记录 IWDT 或复位，停止前取得变化后的应用帧。最终运行时也通过了 ESP-IDF GPIO 唤醒与入口已激活时的拒绝、清除原因对照。

[完整报告](report.md) · [结构化清单](run.json) · [证据及脱敏范围](evidence/README.md) · [先前的留存看门狗复核](../2026-11-18-sticks3-watch-retained-watchdog/)

物理设备、浏览器运行时、功耗、其他唤醒源和整个应用功能留待验证。

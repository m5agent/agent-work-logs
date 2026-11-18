# StickS3 RC_FAST/256 定时深睡

- 日期：2026-11-18（UTC+08:00）。
- 范围：原生 **virtual-device validation**，ESP32-S3 StickS3，冻结 Device Service 1.94.0。
- 结果：**PASS**。两个独立会话各通过两轮定时深睡及正常 HTTP 复位后的两轮复验。八个周期均保留 RTC 数据和计时，数字域内存重新初始化。
- 650 ms 请求的 QMP 实测范围为 659.348–661.286 ms，1,500 ms 请求为 1,504.298–1,511.493 ms。宿主单调接收时钟独立核对了两个范围。第二个会话在读 RTC 寄存器前后均为 `suspended`，慢钟选择为 RC_FAST/256。

[复现与运行报告](report.md) · [结构化记录](run.json) · [有界证据](evidence/d256-deep.summary.json) · [默认慢钟定时深睡历史](../../README.md)

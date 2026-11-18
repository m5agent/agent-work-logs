# Cardputer ADV 固件容量准入的结构化回执

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PASS`（原版固件和原生虚拟设备）
- 问题来源 [Issue #234](https://github.com/m5agent/m5stack-esp-emulator/issues/234)
- 环境 Device Service 1.99.1，Reviewer 候选 0.29.0，macOS 系统 Python 3.9.6

问题 BIN 的文件长度为 2,041,968 字节，启动头和分区布局均要求 16 MiB Flash。Cardputer ADV 板型契约为 8 MiB。Device Service 的两条准入路径均返回 HTTP 409。标准保存快照审核以 `E_STATIC` 结束，候选版在原有「Flash 容量」详情中提供板型容量、固件要求、启动头声明和分区结束地址四项数值。该固件没有执行虚拟写入或获得来宾租约。

同一 Device Service 接受官方 8 MiB UIFlow2 原版。规范化 Flash 恰为 8 MiB，原生来宾正常启动并出帧，证据 ZIP 与该会话一致，停机后释放可写 Flash 和租约。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏证据](evidence/adv-flash-admission.summary.json) · [先前容量复验](../../README.md)

候选验证在隔离环境完成。真机、实物 16 MiB 变体、联网及配对为 `NOT RUN`。Burner 未提交。

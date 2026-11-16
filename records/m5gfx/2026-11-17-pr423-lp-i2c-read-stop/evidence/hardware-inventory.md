# 内部硬件测试中心清单（脱敏摘要）

- 采集时间：2026-11-17 00:16（CST）
- 采集方式：测试中心只读 overview / nodes 接口（端点未公开）
- 脱敏内容：节点 ID、内网地址、端口、固件版本号、任务与 session 标识已全部删除

| 槽位名 | 芯片（报告值） | 在线 | 状态 |
| --- | --- | --- | --- |
| matrix | ESP32 | 是 | idle |
| corep4 | 报告值为 ESP32，夹具为 ESP32-P4 | 是 | idle |
| sticks3 | ESP32-S3 | 否 | offline |
| stopwatch | 未报告 | 是 | idle |
| 未分配设备 | 未报告 | 否 | offline |

结论：没有 ESP32-C5，也没有带 UnitNFC（ST25R3916）的 C5 夹具。因此本 PR 的硬件复现
（read→read、Space B → Space A）无法在本机测试中心执行。

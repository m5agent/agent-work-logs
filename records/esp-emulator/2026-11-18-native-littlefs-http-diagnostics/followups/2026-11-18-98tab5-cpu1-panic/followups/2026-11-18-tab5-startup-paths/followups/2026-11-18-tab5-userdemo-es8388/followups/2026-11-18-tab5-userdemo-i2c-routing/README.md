# Tab5 UserDemo ES8388 的 I²C 路由对照

2026-11-18 · Tab5 · virtual-device validation

| 观察 | 结果 |
| --- | --- |
| 相同重建固件的 ES8388 控制事务 | **PASS（归因）**。GT911 Part 接管 HP I²C0 时 32 次写入全部 NACK。移除 Part 的诊断组中，同一批 32 次写入全部完成，codec 构造返回有效句柄。 |
| 未改动发布版的无 Part 对照 | **PARTIAL**。取到 11 个均匀底色帧，随后 `bsp_touch_new` 返回 `ESP_ERR_INVALID_STATE`。 |
| 完整音频及硬件验收 | **NOT RUN**。这些对照使用默认 I²S0 诊断采集，无 PCM 可用于播放验收。 |

本记录是 [UserDemo 启动断言复验](../../README.md) 的控制器层后续。 [完整执行与证据](report.md) · [机器记录](run.json) · [有界验证摘要](evidence/userdemo-codec-routing.summary.json)

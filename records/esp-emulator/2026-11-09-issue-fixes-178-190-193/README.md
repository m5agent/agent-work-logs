# ESP Emulator 设备目录与原生回归修复

| 字段 | 值 |
| --- | --- |
| 日期 | `2026-11-09`（Asia/Shanghai） |
| 结果 | `PARTIAL`，定向运行与完整平台套件通过，#178/#192 完整负载门槛仍开放 |
| 类型 | `code_change` |
| 源码基线 | `dd2eb35d2e6a909992268089ddc37e27970d4a92` |
| 整合源码 | `42bb6b53dae18265a0e64c4c6775d87c564a07e7` |
| 环境 | 公开资料核对、direct QEMU、隔离 Device Service |

| 问题 | 结果与范围 |
| --- | --- |
| [#190](https://github.com/m5agent/m5stack-esp-emulator/issues/190) | `PASS`，三项设备元数据与官方规格及生成档案一致 |
| [#191](https://github.com/m5agent/m5stack-esp-emulator/issues/191) | `PASS`，SKU、八份公开驱动和文档的 SHA256、五处 blocker 文本核对 |
| [#192](https://github.com/m5agent/m5stack-esp-emulator/issues/192) | `PARTIAL`，StackChan 与 Core2 AXP192 首轮通过，真实超时负控拒绝。两轮完整高负载矩阵待验收 |
| [#193](https://github.com/m5agent/m5stack-esp-emulator/issues/193) | `PASS`，19 项 `PASS/VERIFIED`，哈希不匹配负控按预期 `FAIL` |
| [#178](https://github.com/m5agent/m5stack-esp-emulator/issues/178) | `PARTIAL`，AtomLite 真实 ROM stub 恢复、Core2/StickC、独立服务冷烧录和 host-image 对照通过。完整重复高负载矩阵待验收 |
| [#188](https://github.com/m5agent/m5stack-esp-emulator/issues/188) | `REVIEW`，上游正式版本核对为 0.51.0，DSI PHY 阻塞继续跟踪 |

完整平台 R2 在最终源码运行 2039 项，2029 通过、10 跳过。R1 的 freshness-index 失败单独保留。文档 50 项、Node 30 个脚本、离线 Unit evidence 68 项、四项生成校验及 PR scope 通过。

- [报告](report.md)与[结构化记录](run.json)
- [目录与公开来源](evidence/catalog-summary.json)
- [Classic 虚拟烧录](evidence/classic-flash-summary.json)
- [外设帧与负载](evidence/peripheral-readiness-summary.json)
- [19 项 Unit 运行](evidence/unit-runtime-summary.json)与[源码绑定](evidence/unit-runtime-source-binding-summary.json)
- [验证汇总](evidence/summary.json)

物理硬件、部署、Tab5 新 guest 和两项高负载全量验收属于 `NOT RUN`。本记录固定在源码 PR 前的观察时点，交付结果随实际状态追加。

## 后续交付

- [PR194 交付](followups/2026-11-09-pr194-delivery/)为 `PASS`。#190、#191、#193 已关闭，#178、#188、#192 保持开放。

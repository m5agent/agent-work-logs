# AtomS3 Spirit Level 原版 Reviewer 0.29 复验

- 日期 2026-11-19
- 结果 `PARTIAL`。应用启动和画面通过，互动项待人工复核。
- 工作类型 固件审核和虚拟设备验收。
- 问题来源 [AtomS3 原生显示问题 #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)。
- 源码版本 Device Service `f12b15fb3dc2c27e31b804ccfffd63e8cbce89b8`、Reviewer `69386c6a162a1c786d6745c46eaa330c14558d3c`，以及[已验证的 native QEMU 候选](../../README.md)。
- 运行环境 独立 macOS 原生 Device Service 1.99.2 与 Reviewer 0.29.0，模拟 AtomS3 默认 `m5atoms3-st7735`，禁用访客网络。

## 结果

同一份 Spirit Level 原版 BIN 经保存快照标准重试后，应用就绪从历史 HTTP 408 / `E_NO_FRAME` 变为 HTTP 200。首次就绪无需输入，保存的 128×128 BUBBLE 画面和同会话截帧逐字节一致。随后在 60.009 秒内取样 13 次，启动与画面及虚拟观察均通过。审核仍以 `manual_review / SIM_PARTIAL / E_INTERACTION_CLAIM_PARTIAL` 结束。

## 证据

- 609,856 字节原版 SHA-256 和 8 MiB 规范化 Flash SHA-256 与同一问题的前序验证一致。
- 同一会话的证据 ZIP 通过 CRC 与 8 项成员哈希回读，应用区域匹配原版字节。停止后保留历史，释放 Flash，活动租约归零。
- 描述分类器提出的 `touch_hold_center` 本轮未执行。实机、浏览器、访客网络和常驻路由未测试。Burner 未提交。

[复验报告](report.md) · [运行记录](run.json) · [脱敏证据摘要](evidence/atoms3-spirit-reviewer-029.summary.json)

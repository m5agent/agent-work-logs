# AtomS3 Spirit Level 原版 Reviewer 0.29.1 按键送达

- 日期 2026-11-19
- 结果 `PARTIAL`。启动、画面和三次 GPIO41 按键送达已验证，应用行为断言尚待验收。
- 工作类型 原版保存快照标准 dry-run。
- 问题来源 [AtomS3 #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)与[前序 Reviewer 0.29 复验](../../README.md)。
- 源码版本 Device Service 1.99.3 `86aa77a9`、Reviewer 0.29.1 `3a45e3dd`。
- 环境 独立 macOS 原生 AtomS3 `m5atoms3-st7735`，使用同一签名 QEMU，关闭访客网络。

## 结果

标准快照重试返回 HTTP 202；会话就绪返回 HTTP 200。Reviewer 将原版声明解析为 BtnA 单击、按住 0.6 秒及 2.2 秒。Device Service 接受三项请求，虚拟按键队列记录 120、600 和 2200 毫秒。同一会话的原生 GPIO41 记录验证了三组按下与释放。

可核验实际交付为 `manual_review / SIM_PARTIAL / E_INTERACTION_CLAIM_PARTIAL`。证据保留日常 TUBE 截图和每项动作的前后画面哈希，动作 PNG 未全部保留。两个长按的应用效果待逐项复验。停止后历史保留，Flash 释放，活动租约为零。Burner 未提交。

[复验报告](report.md) · [运行记录](run.json) · [脱敏证据摘要](evidence/atoms3-spirit-reviewer-0291-typed.summary.json)

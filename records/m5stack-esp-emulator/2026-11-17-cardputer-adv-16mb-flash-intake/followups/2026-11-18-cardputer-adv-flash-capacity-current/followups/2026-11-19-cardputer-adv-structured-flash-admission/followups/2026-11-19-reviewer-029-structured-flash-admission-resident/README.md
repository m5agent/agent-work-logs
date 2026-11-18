# Reviewer 0.29.0 常驻上线与旧库存准入

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `LIVE_VERIFIED`
- 问题来源 [Issue #234](https://github.com/m5agent/m5stack-esp-emulator/issues/234)
- 环境 macOS 常驻 Reviewer 与两套原生 Device Service

Reviewer 已切换至 `69386c6a162a1c786d6745c46eaa330c14558d3c`。实际就绪接口返回 HTTP 200，版本为 0.29.0，后端识别为 macOS。130 条审核任务、历史表和抽样证据 ZIP 经独立回读保持一致。工作台和审核设备 Device Service 均继续提供与发布契约字节一致的 OpenAPI 1.99.1。

另用独立的 Device Service 复验历史规范化库存。对要求 16 MiB 的镜像请求创建 8 MiB Cardputer ADV 会话，返回 HTTP 409 `firmware_flash_contract_mismatch`。库内 BIN 和元数据保持原样，没有创建会话或租约。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏回读摘要](evidence/resident-029-flash-admission.summary.json) · [候选版原始路径验证](../../README.md)

Issue #234 已为 `CLOSED / COMPLETED`。生产来宾、真机和 Linux 常驻路由未执行。Burner 未提交。

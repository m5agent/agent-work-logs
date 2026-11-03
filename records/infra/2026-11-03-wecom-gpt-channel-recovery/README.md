# WeCom GPT bridge model and authorization recovery

- 日期：`2026-11-03`（Asia/Shanghai）
- 结果：`PARTIAL`（核心短文本自动回复 `PASS`；旧历史压缩 `FAIL`，recall 重写超时后回退）
- 工作类型：`service_debug`
- 问题来源：用户报告企业微信机器人没有正常回答；无公开 Issue。
- 源码版本：本机部署脚本，无上游 Git base；[修改摘要](evidence/bridge-change-summary.md)记录基线及部署 SHA256。
- 环境：macOS 常驻桥接、WeCom CLI 1.3.0、bot SDK 1.0.7、Codex CLI 0.154.0 / 0.164.0-alpha.11.1。

## 结论

**核心短文本通道已恢复并通过真实用户输入验证：入站消息→GPT 执行→平台接受自动流式回复。** `2026-11-03T06:20:16.561Z` 收到测试，使用 `gpt-6.1-sol/ultra` 完成任务，`06:20:39.163Z` 回复操作成功，约 23 秒。接收端已读及视觉显示未检查。

桥接改用桌面内置 CLI、显式 `gpt-6.1-sol/openai` 和桥接专用 server recall 设置。企微业务权限续期后，会话读取及主动消息提交成功；重启后长连接认证成功。

旧混合 provider 历史仍无法压缩，错误为 `400 array_above_max_length`。保留原会话文件和六个映射备份，当前映射原子清空以创建新的 GPT 会话。server recall 实际装配 8 条上下文（1267 usedTokens），返回 2120 字符；重写超时，普通装配回退正常。以上边界保持独立，整体 `PARTIAL`。

## 关键证据

- [自动回复脱敏摘要](evidence/automatic-reply-summary.json)：真实入站、模型/effort、完成事件、回复时序，以及源日志快照指纹。
- [运行与迁移摘要](evidence/runtime-summary.json)：新会话标记与 usage、旧历史失败、迁移及认证。
- [企微业务接口摘要](evidence/wecom-business-api-summary.json)：续期前错误、续期后会话读取和出站提交。
- [server recall 摘要](evidence/server-recall-summary.json)：装配统计、rewrite timeout 和回退完成。
- [新 GPT 历史分叉摘要](evidence/new-gpt-history-fork-summary.json)：隔离请求完成、源历史和映射未改变；未确认实际远程压缩。
- [脚本修改摘要](evidence/bridge-change-summary.md)：通用改动逻辑、基线及部署 SHA256；全局 Codex/plugin 配置未改变。

## 文件

- [report.md](report.md)：根因、改动、执行与回滚。
- [run.json](run.json)：分层检查与限制。
- evidence：以上经过脱敏的派生摘要，未复制原始消息或身份数据。
- patches：不适用，本机部署脚本没有上游 Git base；提供修改摘要和文件指纹。
- code：不适用，无独立固件工程。

## 未覆盖与未修复项

新 GPT 历史的隔离分叉请求已完成，但未观察显式压缩事件，不宣称远程压缩成功。旧历史压缩仍为 `FAIL`，通过新会话规避；server recall 重写超时，回退正常。接收端已读/视觉显示、长任务跨窗口、媒体收发及并发回归 `NOT RUN`。未声称嵌入式硬件、虚拟固件或物理测量结果。

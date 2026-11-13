# UIFlow2 配对、WebSocket 与浏览器状态修复

- 日期：`2026-11-14`（UTC+08:00）
- 结果：`PARTIAL`。身份持久化、诊断展示和浏览器 304 处理已通过同路径验证；云端控制 PONG 缺失仍导致长连接超时。
- 工作类型：`service_debug`、`code_change`、`report`。
- 问题来源：用户报告 UIFlow2 配对与持续 WebSocket 接收错误；没有公开 Issue 链接。
- 源码：base `ffa621cdcf8422005b7fdf66afdee1be7c5fbba7`；修复已进入 [`main @ a5990e720a8c79310456bf5868141f4cfd50afe8`](https://github.com/m5agent/m5stack-esp-emulator/commit/a5990e720a8c79310456bf5868141f4cfd50afe8)，[对应 CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/43468922515)成功。
- 验证范围：CoreS3 与 Core2 原版固件的原生虚拟设备路径，含浏览器连接原生服务；另有独立主机协议诊断。未做物理硬件验证。

## 当前结论

本次查明三个独立问题。默认虚拟身份被云端以不存在或未绑定拒绝，配对码收到并不等于完成账号绑定；授权身份能够登记并完成文本心跳，但云端没有回复控制 PONG，固件随后因 120 秒超时主动关闭；浏览器 COI worker 还曾因错误构造 304 响应持续报 fetch 失败，使界面与正常运行的 guest 不一致。

修复已提供持久虚拟身份、活跃重复身份保护、独立的配对/WebREPL 观测状态，以及正确处理 304 的 owned worker。同一原版 BIN 的候选 v2 与部署后独立运行各观察 195 秒，UI/身份验收均 PASS。最后一次有 34/34 项验收通过、5855 次取证前 frame 304 正常返回（整会话 5856 次），运行期 API、HTTP、界面和脚本错误均为 0。但仍有 6 次控制 PING、0 次控制 PONG，串口超时 1 次，持续连接 FAIL。因此总体保留 PARTIAL，未宣称已修复云端心跳。

## 关键证据

- [默认身份](evidence/default-baseline-redacted-summary.json)：约 68 秒、20 次有效握手、20 次服务器先发 FIN。
- [授权身份](evidence/authorized-identity-redacted-summary.json)：约 153 秒、5 次关闭前文本往返、4 次控制 PING、0 次控制 PONG，最终 guest 先发 FIN。
- [独立主机复验](evidence/host-control-ping-v2-redacted-summary.json)：Accept 校验通过，12 秒内文本 PONG 1 次、控制 PONG 0 次；属于主机诊断。
- [持久身份](evidence/persistent-identity-redacted-summary.json)：3 次真实 guest 启动包含重启，身份一致；活跃冲突拒绝已验证。[Core2](evidence/core2-persistent-identity-redacted-summary.json)实际收到配对码、MQTT/eFuse 身份一致，但未观察到 WS。
- [部署后功能复验](evidence/browser-postdelivery-redacted-summary.json)、[独立后检查](evidence/browser-postdelivery-postcheck-redacted-summary.json)和[原 ZIP 复算](evidence/browser-postdelivery-guest-redacted-summary.json)：UI PASS，7 次文本心跳、控制 PONG 0 次，持续连接 FAIL；owned guest 与浏览器清理完成。
- [候选 v2 浏览器验收](evidence/browser-candidate-v2-redacted-summary.json)与[同 ZIP 独立复算](evidence/browser-candidate-v2-guest-redacted-summary.json)：UI PASS、持续连接 FAIL；[13 项 Chromium 控制](evidence/coi-final-browser-controls-redacted-summary.json)另列。
- [失败与纠正历史](evidence/browser-failure-history-redacted-summary.json)：保留首次 195 秒 UI PARTIAL、短窗口 910 次 fetch 失败及初始判断纠正。
- [源码交付](evidence/source-delivery-redacted-summary.json)：main 与两次 CI 均绑定同一修复提交；[独立视觉复核](evidence/candidate-ui-independent-visual-summary.json)确认候选最终页面与实际运行态一致。
- [最终主机检查](evidence/final-host-validation-summary.json)：Python 2217 项（8 skip）、50 项文档检查、Node contracts 与四项验证器通过。观察模块另有 24 项测试及 [10 份真实抓包复核](evidence/observer-ten-captures-redacted-summary.json)。

## 文件与边界

[完整报告](report.md)、[结构化记录](run.json)、[离线复现说明](code/README.md)、[摘要生成脚本](code/summarize_private_evidence.py)、[摘要结构](code/summary.schema.json)。产品变更直接由不可变源码链接查阅，本记录不重复附带 patch。

部署后的同路径功能复验已完成。Pages 更新仍为 PENDING，将独立记录。远程 REPL 命令执行、物理硬件和长期连接可靠性没有通过结论。没有提交 Burner。原始 BIN、ZIP、完整串口、截图、配对码、唯一身份和本机部署信息不公开。

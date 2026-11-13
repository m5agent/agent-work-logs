# Pages 本地完整资格验证与精确归档包

- 日期：`2026-11-14`（UTC+08:00；执行时间见 run.json）。
- 结果：`PASS`，限本地 browser-WASM 完整资格与归档包；release、Pages 发布及实际 HTTPS 验证 `NOT RUN`。
- 工作类型：`report` / virtual-device validation。
- 问题来源：[身份能力与 COI 修复跟进](https://github.com/m5agent/agent-work-logs/tree/02ecde371901c8f97d5746eaab0ee7182b56cf5c/records/esp-emulator/2026-11-14-uiflow-cloud-websocket/followups/2026-11-14-identity-capability)。
- 源码：[m5stack-esp-emulator @ 70ef503fc2fb8b2c787fa9065e2952f525c40099](https://github.com/m5agent/m5stack-esp-emulator/blob/70ef503fc2fb8b2c787fa9065e2952f525c40099/platform/tests/test_public_qemu_admitted_boards.mjs)。
- 环境：完整静态导出、Google Chrome `157.0.8103.52`、硬件 ANGLE、串行 browser-WASM；不使用 Device Service。

## 结论

固定站点 `54fc8d8fe023ef0d86e3bfdea3d3db37599a2f59404c54fdb8920d466bd14a8c` 的 23 款准入设备完成全部 72 例：
23 编辑器、23 按钮、Cardputer ADV 键盘、StackChan 机身触摸与 24 fixed 示例。
全部终态 PASS、子进程正常退出，2993 项检查通过，0 重试、0 跳过、0 NOT RUN。
另有 1 个原版 CoreMatrix stock guest，以及 5 项 pixel 和 13 项 COI host 控制；
这 18 项 host 控制不计入 guest 数量。

42 个浏览器运行资产与之前发布资产相同，本轮未重建 WASM。精确归档包有 2179 个普通文件，
逐项字节与已验证导出闭集一致。它已经具备本地资格，尚未发布；不据此更改历史 hosted
完整门禁的 FAIL/PARTIAL 结论。

## 关键证据

- [完整资格与 Chrome 来源](evidence/qualification-gates-summary.json)：72 例、75 份含前置的子报告闭集、393 次浏览器抽样。
- [独立终态审计](evidence/final-independent-summary.json)与[最终清理](evidence/cleanup-terminal-summary.json)。
- [归档包](evidence/package-summary.json)：186574444 字节，SHA256 `8c25e92e124fc0d323afd51b13c8ce05719e54167c1cbc5d1a3507eab28b9b98`。
- [48 例 UI 独立证据](evidence/completed-ui-independent-summary.json)与[24 例 fixed 独立证据](evidence/fixed-independent-summary.json)。
- [历史状态](evidence/history-summary.json)：旧源码 44 PASS / 28 NOT RUN、运行中 checkpoint 观察误判与最终状态分别保留。

## 文件

- [report.md](report.md)：背景、执行、结果及边界。
- [run.json](run.json)：结构化结果及全部有界 evidence 哈希索引。
- `evidence/cases-1-summary.json` 至 `cases-12-summary.json`：逐例固件、runtime、ROM、controller、输入、输出及清理。
- [code/README.md](code/README.md)：固定源码 runner、实际参数及复现步骤。
- patches：不适用；本记录执行既有固定 runner，没有新增产品补丁。

本记录不复制原 BIN、ROM、Flash、原始截图、串口全集、会话/Worker 标识或本机路径。
有界摘要记录原报告及实际输出哈希，不将删减后的内容称为 raw。

## 未覆盖项

总 75 份报告中 72 份记录自身浏览器版本，3 份未记录（COI 与 2 个 CoreS3 fixed）。
它们由同一包装流程的实际可执行文件绑定，未补写原报告缺字段；393 次采样不是连续监控。
额外 stock CoreMatrix 的 pthread-before-iframe 证据仍为 `NOT CAPTURED`。
本地资格不等同实际 HTTPS 交付。WASM 不继承 native C6 GPIO 或云端网络修复；native 云端
控制 PONG 缺失仍为独立 FAIL。物理硬件、RF、功耗和 Burner 提交均不在本记录通过范围。

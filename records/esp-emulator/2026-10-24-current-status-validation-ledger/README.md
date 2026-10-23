# ESP Emulator Current Status and Validation Ledger

- 日期：`2026-10-24`
- 结果：`PASS`（文档、代码地图与契约测试）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`aeb21e2027c3b821098e680fa5cb163d04ed7eec`
- 基线版本：`689c49b77ff6595a97dc57d3b3e6b37bef7fde8d`
- 环境：macOS Apple Silicon；Python 3；Node.js；无 QEMU 功能运行

## 结论

当前状态、历史验证、未完成 Backlog 和代码入口已经拆成四个单一职责页面：

- `docs/project-status.md`：只回答当前能做什么、风险和尚未闭合的边界；
- `docs/validation-ledger.md`：按日期保存当时里程碑、检查项和 evidence；
- `docs/project-backlog.md`：只保存未完成任务、依赖和验收；
- `docs/code-map.md`：按服务、固件、网络、运行时/设备组织代码与测试入口。

同时修正了 Core2 `HCI-3a` 的表述：它是诊断性单包 C2H 证据，不是可扩展的
产品 controller-to-host 后端。`HCI-3b`、`HCI-4`、GDB 控制面移除和
bit-exact controller 仍未完成。

## 关键证据

- 平台测试：`264/264 PASS`，0 skipped；
- runtime coverage、peripheral catalog、QEMU profiles：全部 `PASS`；
- Node SHA256/upload client：`2/2 PASS`；
- Python compileall：`PASS`；
- 文档契约：索引、链接、API 版本、设备计数、测试计数、旧状态、缺失完成日志
  和 evidence JSON 解析全部 `PASS`；
- GitHub Actions：run `40038712285` 成功；
- 物理硬件、RF、完整 QEMU 功能矩阵：本轮 `NOT RUN`。

## 文件

- `report.md`：改动范围、验证命令和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：公开脱敏的本地验证摘要；
- `evidence/github-actions.summary.json`：对应源码 commit 的 CI 回读。

## 未覆盖项

- 本轮没有重跑 67-case 外设矩阵；
- 没有新的 QEMU session 或固件功能结论；
- 没有物理硬件、RF、功耗、声学、光学或机械验证；
- `NET-04`、`NET-05`、`CORE2-01`、`CORE2-02`、`FW-01..03`、
  `SVC-01..03`、`HW-01`、`TAB5-01`、`UI-01`、`CZ-01` 仍未完成。

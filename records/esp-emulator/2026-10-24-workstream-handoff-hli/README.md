# ESP Emulator 工作流交接与 Core2 HLI 诊断归档

- 日期：`2026-10-24`
- 结果：`PASS`（文档、代码卫生与证据契约）
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`543f900225457c6b7cbd03f30a3ef01844119359`
- 基线版本：`7d274bcf3b8f7759f4d0d721bd6b234f6a67a928`
- 环境：macOS Apple Silicon；Python 3；Node.js 22；现有 QEMU 虚拟设备与静态证据

## 结论

把当前工程状态重新收敛到同一组入口：

- `workstreams.md` 新增可直接交接的 P0 摘要、当前实现、验证面和下一动作；
- `project-status.md`、Backlog、代码地图、网络方案、QEMU 矩阵和统一运行时
  同步 Core2 native-HCI 的最新阶段；
- 新增 HLI queue 诊断 evidence：guest firmware ISR/controller task 能消费
  QOM 投递的 event-13 marker，但这只证明交付 seam，不证明真实 HCI event、
  ACL、GATT 或完整后端；
- 清理 6 个 Python 未使用导入/局部变量，并用全平台测试和静态检查验证。

本次不新增 Device Service、QEMU 或固件功能，不改变虚拟设备能力。

## 关键证据

- 平台测试：`267/267 PASS`；
- GitHub Actions：平台契约与 Linux namespace/egress 两个 job 均 `PASS`；
- WebBurner SHA256/upload client：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- 文档索引、相对链接、日期、API 版本、旧状态与 evidence JSON：`PASS`；
- Python `compileall`：`PASS`；
- Ruff `F401/F821/F822/F823/F841`：`PASS`；
- 现有完整 QEMU 矩阵仍为 `67/67` case、`274/274` check；本次未重跑；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：范围、关键判断、验证和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：聚合验证结果
- `evidence/hli-queue-diagnostic.summary.json`：HLI 诊断和限制摘要

## 未覆盖项

- HLI 只投递了 event-13 marker，没有真实 Reset Complete、ACL、ACK 或 GATT；
- 实验代码未保留，不能从提交后的工作树直接复现；
- `HCI-3b`、`HCI-4`、GDB 控制面移除、bit-exact BT controller 和物理
  cache/PSRAM 等价性仍开放；
- 远程 worker、活动 QEMU re-attach、IPv6、运行时权限/许可和真机安全配置
  仍开放；
- 不把 virtual-device validation 写成 RF、功耗、光学、声学或机械测量。

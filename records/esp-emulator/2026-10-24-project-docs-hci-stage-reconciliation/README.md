# ESP Emulator 文档新鲜度与 Core2 HCI 阶段重整

- 日期：`2026-10-24`
- 结果：`PASS`（文档、契约和回归入口层）
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`53cefc14e909519baebf12784597c3274f72f1e4`
- 基线版本：`7f8343d0b3c5e0ecfac90d24084e250c0ad5a5f9`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40012704195>
- 环境：macOS Apple Silicon；GitHub Actions Ubuntu；Python 3；现有 QEMU/网络证据

## 结论

把当前事实、三组 P0、Core2 native-HCI 的四个阶段和历史调查页重新对齐到
同一份可检查台账。主要修正包括：

- 把错误的 `243/243 PASS` 改成准确的 CI 快照：`243` 项测试中 `241` 项
  通过、`2` 项环境相关跳过；本机完整套件为 `Ran 243 tests`、`OK`；
- `docs/` 下全部 `30` 个 Markdown 页面进入新鲜度台账，`29` 个非导航页
  都有文档类型、最近核对日期和事实基线；
- Core2 native-HCI 明确拆为 `HCI-1 PASS`、`HCI-2 PARTIAL`、
  `HCI-3 OPEN`、`HCI-4 OPEN`；
- 记录 `vhci_send` 直接注入实验失败：函数返回后 guest 仍等待 ack 并
  `ETIMEDOUT`，因此不再猜函数参数，下一步转向真实
  controller-to-host notification/queue 语义；
- 将当前执行顺序收敛为 `HCI-3 → HCI-4 → NET-03/NET-04 → FW-01`。

本次没有修改 QEMU 控制器、固件数据面、Device Service 运行逻辑或网络策略。

## 关键证据

- 本机平台套件：`243` tests，`OK`；
- GitHub Actions：`Ran 243 tests`、`OK (skipped=2)`，两个 job 均成功；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- 全部 docs 索引/日期、Markdown 相对链接和旧状态语句检查：`PASS`；
- Python entry point 编译：`PASS`；
- 本次改动：`22` files、`261` insertions、`61` deletions；
- QEMU 全矩阵、设备功能重跑和物理硬件：`NOT RUN`。

## 文件

- `report.md`：整理范围、关键判断、验证和回滚；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：聚合验证结果。

## 未覆盖项

- 不新增 virtual-device 或 hardware validation；
- 不证明 C2H 已交付、完整 H2C sequence、外部 GATT 或 repeated lease；
- 不证明物理 cache/PSRAM、BT controller/baseband、RF 或功耗等价性；
- 不在 docs-only 变更中重跑 67-case QEMU 全矩阵。

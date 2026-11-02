# ESP Emulator virtual-device-first validation policy

- 日期：`2026-11-02`
- 结果：`PASS`
- 工作类型：`code_change`（documentation/contracts only）
- 问题来源：用户明确说明 validated virtual device 是主力验证路径，要求删除
  Tab5 的真机前置要求
- 源码版本：`m5agent/m5stack-esp-emulator`
- PR：[#79](https://github.com/m5agent/m5stack-esp-emulator/pull/79)

## 结论

Tab5 专属的 `real-hardware validation before production-ready external claim`
要求已从项目文档删除。项目级 `HW-01 真机同路径` P0、workstream、依赖和 Task
索引也已移除。

全局 `~/.codex/AGENTS.md` 本来就没有 Tab5 真机要求，而且已经写明
validated virtual device 可满足同一实现路径的发布门禁，因此全局文件未改。

保留的唯一硬件条件现在是 claim-scoped：只有发布结论明确声称 RF、功耗、
声学、光学、机械或电气属性时，才要求对应的 `hardware validation`。虚拟
设备结果仍必须标为 `virtual-device validation`，不能冒充物理测量。

## 关键证据

- Tab5 deferred backlog 删除生产就绪前的 real-hardware 条件；
- `HW-01` 从 Backlog、Status、Workstreams、Engineering Handoff 和生成快照移除；
- 文档契约 `50/50 PASS`；
- `project_snapshot.py --check` 为 `PROJECT_SNAPSHOT_OK`；
- `git diff --check` PASS；
- PR head `4/4` CI checks PASS；
- PR #79 合并为 `8dd390ff`，merge main CI `41396758444` 两 job PASS。

## 文件

- `report.md`：项目/全局口径核对、改动和边界
- `run.json`：结构化记录
- `evidence/validation-summary.json`：验证结果和策略摘要
- `patches/`：不适用；文档改动由 PR #79 提供
- `code/`：不适用；契约测试位于源码仓库

## 未覆盖项

- 没有运行 QEMU、esp-emu、固件矩阵或物理设备；这是文档/契约变更。
- Tab5 的 CSI、I2S/PCM、USB Host、SDIO、动态 I2C 和控制器级触摸仍为
  `partial`，删除真机前置要求不等于宣称这些模型已闭环。
- RF、电气、光学、机械、声学和功耗结论在明确声称时仍需要物理证据。

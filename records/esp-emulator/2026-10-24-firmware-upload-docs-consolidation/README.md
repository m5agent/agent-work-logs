# ESP Emulator 固件上传可靠性、代码与文档总整理

- 日期：`2026-10-24`
- 结果：`PASS`（服务契约、回归和文档层）
- 工作类型：`code_change`
- 问题来源：用户要求完整整理当前代码和文档，并重新梳理已完成工作与待办
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码基线：`5217b50af60c7ac31f3051a6fef8b70fdb110fe4`
- 结果提交：`0ffaf07b334a09690e2ad62b23078c04ea8b134c`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40021209492>
- 环境：macOS Apple Silicon 与 GitHub Actions Ubuntu；Python 3；现有 QEMU/网络证据

## 结论

完成一次代码、契约、证据和文档的联合对账，并补齐可恢复 chunk upload 的
可靠性边界：

- 每次 append 在 staging 写入和 metadata 提交都成功后才算确认；
- 写入、`fsync` 或 metadata 提交失败时，staging 截断回最后一个确认 offset；
- metadata 使用原子替换；
- abort、孤立 staging 和过期 upload 记录由 storage janitor 清理；
- HTTP 增加可查询续传进度、删除和失败状态测试；
- 修正 `platform/README.md` 中仍把 `HCI-3` 整体写为未完成的旧口径；
- 移除已漂移的测试计数、CI run、基线和源码行数，统一按当前证据表述；
- 新增能力成熟度表，把虚拟设备验证、本地服务化、真机三层分开。

本记录不产生新的 QEMU 设备功能 PASS。WebBurner UI 接线、Core2
`HCI-3b/HCI-4`、双设备 network fabric、worker 生命周期和物理硬件仍开放。

## 关键证据

- 本机：`Ran 249 tests`、`OK`，无跳过；
- GitHub Actions：`Ran 249 tests`、`OK (skipped=2)`，两个 job 均成功；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- OpenAPI：`3.1.0`，API `1.12.0`，`37` 条路径；
- upload evidence 的 checks 全为 true；
- 本次改动：`19` files、`1213` insertions、`72` deletions；
- QEMU 全矩阵、设备功能重跑和物理硬件：`NOT RUN`。

## 文件

- `report.md`：问题、代码改动、验证和剩余工作；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：本机与 CI 聚合结果；

## 未覆盖项

- 没有重跑 67-case QEMU 全矩阵，因为本次没有修改 QEMU 模型或设备数据面；
- WebBurner 页面的进度、重试、取消和刷新恢复仍为 `NOT RUN`；
- Core2 `HCI-3b` 完整 HCI/GATT 与 `HCI-4` repeated lease 仍为 `OPEN`；
- 网络双设备 fabric、自托管 worker、外部 IPv6 未完成；
- 物理硬件验证仍为 `NOT RUN`。

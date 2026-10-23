# ESP Emulator 当前基线、代码地图与 Backlog 重整

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`26090ceb868c66a6b0c338c41f7d242d243f1be2`
- 基线版本：`eca4120090ad46b12b64ff74b345c38def80804b`
- 环境：macOS Apple Silicon；Python 3；现有 QEMU/Tab5/Linux evidence

## 结论

完成一次从代码、catalog、profile、平台测试和现有 evidence 反推当前文档的
全量重整：

- 当前能力、Backlog、代码地图、网络方案和固件清单统一到同一快照；
- `project-backlog.md` 收敛为只含未完成工作、依赖和验收条件；
- 增加文档新鲜度台账，给历史调查页加醒目的历史边界；
- 修正 Core2 OpenMAC/BLE 补丁页仍把 DNS、公网和 BLE 写成未验证的旧结论；
- 修正 Core2 “cache panic” 的旧归因，统一为 interrupt-WDT/timer starvation
  的已缓解边界；
- 更新 catalog/profile 生成时间和 Core2 blocker 表述；
- 扩展文档契约测试，阻止旧状态、错误日期和 Backlog 完成日志回写。

本次为文档与生成元数据整理，没有修改 QEMU 控制器、固件数据面或 Device
Service 运行逻辑。

## 关键证据

- 平台测试：`225/225 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- `git diff --cached --check`：`PASS`；
- 所有 `docs/**/*.md` 进入索引、相对链接检查：`PASS`；
- 设备计数：14 台登记、12 个 QEMU ESP32 profile、13 个 `/api/v1` 可管理设备；
- 最新已有全矩阵 evidence 仍为 `67/67` case、`274/274` check；
- 本次没有重跑 QEMU 全矩阵，物理硬件：`NOT RUN`。

## 文件

- `report.md`：改动范围、验证和边界
- `run.json`：结构化记录
- `evidence/verification.summary.json`：聚合验证摘要

## 未覆盖项

- 不产生新的 QEMU、网络、固件或真机功能 evidence；
- 不改 Core2 GDB bridge、BT controller、Tab5 外设或网络策略实现；
- FAT/SPIFFS、DHCP renewal、egress IP/port policy 等仍为 Backlog；
- RF、功耗、声学、光学、机械和电气等价性仍需真机验证。

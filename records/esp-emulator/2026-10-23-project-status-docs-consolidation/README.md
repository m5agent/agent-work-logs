# ESP Emulator 项目状态与文档收敛

- 日期：`2026-10-23`
- 结果：`PASS`（代码/文档一致性与测试）
- 工作类型：`documentation_and_maintenance`
- 源码版本：`m5agent/m5stack-esp-emulator @ 67c0aa4`
- 基线版本：`6bcd6e8`

## 目标

整理长期增量开发后出现漂移的 README、AGENTS、网络文档、设备档案和后端说明，
把“当前能力”“未完成工作”“实现原理”和“验证证据”拆成明确职责。

## 结论

- 新增单一当前状态页，集中记录设备矩阵、unified runtime、最新矩阵和平台测试；
- Backlog 重写为只包含未完成事项、优先级和依赖；
- 修正 README/AGENTS 中“网络尚未接入”“全矩阵未跑”等过期结论；
- 将 `qemu-unified` 统一为规范 runtime，`qemu-ble` 明确为兼容别名；
- NanoC6 从 `boot-capable` 修正为 `headless-ready`，并加入 schema/generator/
  test 支持；
- 六个 S3 设备的生成档案补齐 unified WiFi/BLE 和外设验证范围；
- 增加生成目录一致性和文档链接/旧结论检查，防止后续再次漂移。

## 关键证据

- 平台测试：`182/182` PASS；
- runtime coverage、peripheral catalog、QEMU profiles check：PASS；
- 生成设备档案与 `catalog.source.json` 一致；
- README、AGENTS、docs 和生成设备 README 的相对链接全部存在；
- 本次不改 QEMU/板级模型，因此未重新运行 67-case 全矩阵；最近一次
  `67/67`、`274/274` PASS 的结果仍作为设备功能基线；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：问题、改动范围、验证和边界
- `run.json`：机器可读结果
- `evidence/verification.summary.json`：测试与一致性检查摘要

## 未覆盖项

本次不新增外设模型，不关闭 Core2 cache 稳定性、Tab5 缺失数据面、网络 namespace/
pcap 或真机验证。相关事项已归入项目 backlog。

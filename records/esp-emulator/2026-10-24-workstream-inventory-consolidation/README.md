# ESP Emulator 工作流台账、代码地图与任务索引重整

- 日期：`2026-10-24`
- 结果：`PASS`（文档与契约层）
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`3403287`
- 基线版本：`71ab6ef`
- 环境：macOS Apple Silicon；Python 3；现有 QEMU/Tab5/Linux evidence

## 结论

把当前项目的 12 条主要工作流整理为同一份可执行台账，补齐每条工作流的代码面、
证据入口、当前状态和未完成 Task ID。同步修正四处与后续实现不一致的旧说明：

- 精确 IPv4 IP/协议/端口 egress、veth/NAT 已实现，不再写成完全开放；
- DHCP renewal 已进入网络和服务架构说明；
- LittleFS/FAT12/16/32 文件清单已完成，SPIFFS 和权限/许可策略仍开放；
- QEMU 适配矩阵区分 2026-10-23 板级验收与 2026-10-24 全矩阵回归。

同时补全 `platform/tools/` 的 24 个顶层工具清单、测试入口归属和代码组织债务，
并新增文档门禁：新增平台工具或 Backlog Task ID 却未同步索引时测试会失败。

本次没有修改 QEMU 控制器、固件数据面、Device Service 运行逻辑或网络策略实现。

## 关键证据

- 平台测试：`236/236 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- Markdown 索引、相对链接、API 版本、旧状态和 Task ID 一致性：`PASS`；
- `git diff --check`：`PASS`；
- 本次未重跑 67-case QEMU 全矩阵，直接引用既有 `67/67`、`274/274` evidence；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`：整理范围、代码结构判断、验证和回滚；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：聚合验证结果。

## 未覆盖项

- 不产生新的 virtual-device 或 hardware validation；
- 不声称 WiFi/BLE 具备 RF、天线、安全模式或功耗等价性；
- 不在本次文档里程碑中进行 6700 行 Device Service 的高风险拆分；
- `SVC-03` 只登记拆分顺序和验收条件。

# ESP Emulator 当前基线、代码地图与验证元数据收口

- 日期：`2026-10-24`
- 结果：`PASS`（文档、契约、回归入口与交付层）
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`730123da116ece1acbd97744de419e97596f0232`
- 基线版本：`ca2030502b46c9cc67daab6c13919a4bf541fd84`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40061751714>
- 环境：macOS Apple Silicon；GitHub Actions Ubuntu；Python 3；Node.js

## 结论

本轮没有修改 QEMU 数据面或设备功能，而是把快速变化的项目事实收敛成可持续
维护的结构：

- README、文档导航和工作流台账不再复制平台测试数与全矩阵计数；当前值只由
  `docs/project-status.md` 维护，历史值只追加到 `docs/validation-ledger.md`；
- 设备 catalog 与 QEMU profile 的验证日期/状态增加自动交叉校验；
- 新校验实际发现并修正了两处旧元数据：AtomS3R 仍停在 `2026-10-20`，
  PaperMono 仍写成 `display-input` 而不是 `display-touch`；
- 明确 `backend-required` 是 CardputerZero 的固件族分类，不等于该设备后端未
  实现，也不等于整体完成度；
- 记录当前代码债务：`device_service.py` 编排热区、大型 service 契约测试和
  混载的文档一致性测试；
- 同一推送范围包含前一个本地提交的 Core2 `3×60s` hold evidence；该结果由
  既有 evidence 提供，本轮没有重新运行 QEMU。

## 当前代码与验证基线

- 14 台设备已登记；
- 12 台 QEMU-backed ESP32 与 Tab5 可由 Device Service 创建；
- 13 台设备的登记外设达到 `simulated`，Tab5 仍为 `partial`；
- CardputerZero 使用独立 Linux ARM64 后端，整体状态仍为 `PARTIAL`；
- 当前规范无线入口是 `runtime=qemu-unified`；
- Core2 规范 profile 是 `core2-native-hci`，旧 `core2-native-vhci` 仅作
  GDB 诊断/兼容；
- 所有结果均为 virtual-device validation；物理硬件仍为 `NOT RUN`。

## 当前待办

| 优先级 | Task | 下一项 |
| --- | --- | --- |
| P0 | `NET-04` / `SVC-01` | 跨主机 executor/reattach、TLS/mTLS、credential rotation、companion/evidence continuity、生产多机调度 |
| P1 | `NET-05` | 外部 IPv6 exact endpoint、veth/route/NAT 与清理 |
| P0 | `FW-01` → `FW-03` → `FW-02` | 运行时权限/完整许可、跨厂商样本、真机 key/eFuse |
| P1 | `CORE2-02` | 多小时 soak、重复 GATT reconnect、WiFi/BLE coexistence，再评估 bit-exact controller 与物理 cache/PSRAM |
| P2 | `SVC-02` / `SVC-03` | warm pool、配额、对象存储、审计和多机容量；按 API/evidence 边界拆 `device_service.py` |
| P1 | `TAB5-01` / `UI-01` / `HW-01` | Tab5 P4 数据面、逐设备视觉保真和同固件 SHA 真机验证 |
| P2 | `CZ-01` | CardputerZero 系统、驱动、USB/网络竞态和长期回归 |

## 关键证据

- 本机平台套件：`297/297 PASS`，0 skipped；
- runtime coverage、peripheral catalog、QEMU profiles：全部 `PASS`；
- Node SHA256/upload client：`2/2 PASS`；
- Python compileall、改动文件 Ruff、`git diff --check`：`PASS`；
- GitHub Actions：platform contracts 与 Linux network namespace policy 均
  `success`；
- 完整 UIFlow2 外设矩阵：`NOT RUN`（本轮为文档/元数据整理）；
- 物理硬件、RF、电气、功耗、声学、光学和机械验证：`NOT RUN`。

## 文件

- `report.md`：整理范围、发现、验证结果、风险和回滚；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：本地与 CI 聚合证据；
- `evidence/github-actions.summary.json`：CI run/job 回读；
- `patches/`：不适用，修改已进入源码仓库；
- `code/`：不适用，回归代码位于源码仓库。

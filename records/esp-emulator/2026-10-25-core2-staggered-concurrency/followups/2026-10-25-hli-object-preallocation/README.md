# ESP Emulator Core2 HLI object preallocation and current-state reconciliation

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`8243850b27fbff420560fcba67c06fae913e83bc`
- 结果版本：`bf98ea8d00dd759da9db44100e239c692f6143ee`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40174318654>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；QEMU virtual device；
  无物理硬件

## 结论

上一 follow-up 已用 `0007` 清除 observed-invalid HLI scheduling，但独立复核
仍会在无错峰双实例冷启动中触发 `ble_hs_hci_process_ack`
`LoadProhibited`。本 follow-up 将其定位为投递延迟：

- Bumble 已在约 `4.6ms` 内返回 Command Status/LE Meta；
- 旧路径需要 CPU0 执行 guest allocator/`os_mbuf` nested guest call 才能把
  packet 放入 HLI queue；
- ACL FIFO head 使 Command Status 接收→HLI 延迟约 `3.660s`，超过 NimBLE
  `BLE_HCI_CMD_TIMEOUT_MS=2000`；
- `0008` 在 CPU0 idle 时预分配两个真实 guest HCI event buffer 和两个真实
  ACL mbuf；CPU0 busy 时直接填充 guest 对象并投递真实 HLI callback；
- 未使用固定 ACK、host Python 假值或 guest queue 绕过；无 spare object 时
  仍回退到原 halted/idle guest-call 路径。

结果为两批独立无错峰 `4×120s`，每批 `4/4 PASS`，合计 `8/8 PASS`。每
lease 36 events/9 ACLs 全部走 fast path、event/ACL spare depth 均为 2、
HLI `45/45`、`hli-errors=0`、`hli-prealloc-failures=0`，无 scheduler
reset 或 panic；trace ACK event 延迟降至约 `0.328s`。

本次同时重整了当前状态、Backlog、API 契约、网络/Core2 专题、generated
catalog 和自动项目快照。`CORE2-02` 明确回到当前 goal 的 `P0`，执行顺序统一
为“网络 → Core2 → 固件安全/Manifest”；历史 `0007` 失败和最终 `0008`
PASS 分开保留。

## 关键证据

- 平台测试：`463/463 PASS`；
- 文档契约：`36/36 PASS`；
- QEMU profiles：`19/19 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- Core2 device group：`6/6 PASS`；
- 完整 UIFlow2 外设矩阵：`67/67` case、`274/274` check，全部首轮无重试；
- Core2 六个 matrix case：`24/24` check PASS；
- 两批独立无错峰 `4×120s`：`8/8 PASS`；
- H4 transport targeted test：`PASS`；
- coverage/catalog/profile/snapshot、Ruff `E9/F`、compileall、
  `git diff --check` 和 `0008` reverse-check：`PASS`。
- GitHub Actions `40174318654` 的 `platform-contracts` 与
  `network-namespace-policy`：`PASS`。

固件 SHA-256：
`5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
ELF SHA-256：
`5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
QEMU SHA-256：
`f2bc2b4d5e4a5a8a0a8b3b4cf3ccd36ea2a67f44a57413bc7c575b304e2159e5`。

## 文件

- `report.md`：根因、实现、代码/文档对账、验证和回滚；
- `run.json`：机器可读执行结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `patches/0008-esp32-native-hci-preallocate-hli-objects.patch`：QEMU 修复。

原始 session evidence 与完整矩阵脱敏汇总已提交在公开源码仓库结果版本：
[`tests/uiflow2/core2_native_hci/`](https://github.com/m5agent/m5stack-esp-emulator/tree/bf98ea8d00dd759da9db44100e239c692f6143ee/tests/uiflow2/core2_native_hci)。

## 未覆盖项

- 两个以上实例的更高并发和持续吞吐；
- active-stop 之外的其他 teardown 模式；
- bit-exact Espressif BT controller/baseband；
- 物理板载 PSRAM/cache timing；
- RF、功耗、电气、声学、光学和机械；
- physical hardware validation。

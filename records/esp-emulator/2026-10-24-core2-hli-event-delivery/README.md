# ESP Emulator Core2 HLI 真实 HCI Event 交付

- 日期：`2026-10-24`
- 结果：`PASS`（窄路径 virtual-device）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`acd5329c4fecb23d7ac2cb1e5dd6dcf370c673f5`
- 基线版本：`543f900225457c6b7cbd03f30a3ef01844119359`
- 环境：macOS Apple Silicon；QEMU `m5core2`；stock UIFlow2 v2.5.3；Bumble external HCI peer

## 结论

用 firmware 自己的 `BTDM_CTRL_HLI` queue/meta queue 和 `INTSET[29]` 交付
真实 HCI Reset Complete，取代仅执行 `ets_printf` 的 marker。

- QEMU 调用 guest `ble_transport_alloc_evt(0)` 分配池化 event buffer；
- 写入不含 H4 type byte 的 `0e0401030c00`；
- event 13 work item 在 firmware controller task 中调用
  `ble_transport_to_hs_evt_impl`；
- guest 从 HCI Reset `01030c00` 前进到 Read Local Version `01011000`；
- 独立运行连续 `5/5` PASS。

该结果关闭了 HLI 真实 command event 的窄路径，但不是完整 HCI/GATT：
ACL、controller ACK/flow-control 和完整 controller transaction 仍未完成。

## 关键证据

- 源码测试：
  `tests/uiflow2/core2_native_hci/test_hli_event.py`；
- evidence：
  `tests/uiflow2/core2_native_hci/evidence-2026-10-24-hli-event-5x.json`；
- QEMU patch：
  `patches/qemu-core2-native-hci/0002-esp32-native-hci-hli-event.patch`；
- patch SHA256：
  `0525e5b8f3a81241de919e3cb4c092a3aa5a6ab395de5ee2b85d714cf8f7c518`；
- GitHub Actions `40044998540`：全部成功；
- 平台 `267/267`；runtime coverage、peripheral catalog、QEMU profiles PASS。

## 文件

- `report.md`：实现、复现、边界与失败 follow-up
- `run.json`：结构化记录
- `evidence/verification.summary.json`：环境、运行和检查摘要

## 未覆盖项

- 只验证 Reset Complete，不验证 ACL 或完整 GATT；
- Bumble peer 未完成 advertisement discovery；
- 没有 Device Service repeated lease；
- 没有 bit-exact Espressif BT controller/baseband；
- 物理硬件、RF、功耗和 cache/PSRAM 时序仍为 `NOT RUN`。

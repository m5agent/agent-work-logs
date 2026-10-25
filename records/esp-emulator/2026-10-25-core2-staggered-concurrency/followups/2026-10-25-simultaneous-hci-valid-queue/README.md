# ESP Emulator Core2 simultaneous HCI delivery and documentation reconciliation

- 日期：`2026-10-25`
- 结果：`PARTIAL`（virtual-device validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`e3c5d089c33397c1948fb611e776d75cb3c20bd8`
- 结果版本：`8243850b27fbff420560fcba67c06fae913e83bc`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40170434652>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；QEMU virtual device；
  无物理硬件

## 结论

无错峰 Core2 native-HCI 并发已从“单一 guest panic”细化为两个独立问题：

- extended BLE GATT request/notification timeout 扩到 `30s`，消除一部分过早
  peer 超时；
- QEMU `0007` 仅在最近一次 poll 观察到有效 guest scheduler/meta queue 后
  安排 HLI 投递，消除了旧四 lease 运行中的 `hli-errors=3`。

当前实现的首批四个无错峰 `120s` lease 为 `4/4 PASS`，每轮 HLI `45/45`、
`hli-errors=0`，并完成 WiFi、公网、NUS GATT、PSRAM、frame/QOM、pcap、
bounded TCG、evidence 和 cleanup。

但独立复核的首个并发批仍有一个 guest 在
`ble_hs_hci_process_ack` (`0x402630cc`) 触发 `LoadProhibited`；runner
保留 partial evidence 并以 aggregate `FAIL` 停止，没有重试掉失败。因此
HLI valid-queue gate 是有效局部修复，但 no-stagger cold-start stability
仍是 `OPEN`。

## 关键证据

- 平台测试：`462/462 PASS`；
- 文档契约：`36/36 PASS`；
- QEMU profiles：`19/19 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  Ruff `E9/F`、compileall、patch reverse-check、`git diff --check`：`PASS`；
- 30 秒错峰并发历史基线：`2/2 PASS`；
- 新实现无错峰首批：`4/4 PASS`；
- 新实现独立复核：`1 PASS / 1 FAIL`，失败 guest panic 保留。

## 文件

- `report.md`：代码改动、失败分类、文档收口和验证边界；
- `run.json`：机器可读执行结果；
- `evidence/verification.summary.json`：不含设备标识的验证摘要；
- `patches/0007-esp32-native-hci-require-valid-guest-queue.patch`：
  QEMU valid-guest-queue gate。

原始 session evidence 已提交在公开源码仓库结果版本的
`tests/uiflow2/core2_native_hci/`。

## 未覆盖项

- no-stagger cold-start stability 尚未关闭；
- 更高并发、持续吞吐和更多 teardown 模式；
- bit-exact Espressif BT controller/baseband；
- 物理 PSRAM/cache timing、RF、功耗和电气；
- physical hardware validation。

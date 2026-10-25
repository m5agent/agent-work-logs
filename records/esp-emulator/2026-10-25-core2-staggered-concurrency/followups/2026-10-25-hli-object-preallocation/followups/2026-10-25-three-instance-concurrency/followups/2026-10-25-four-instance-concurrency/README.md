# ESP Emulator Core2 four-instance concurrency and work-document reconciliation

- 日期：`2026-10-25`
- 结果：`FAIL`（virtual-device validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`db46335e7f71f035ce4a1461567ffb256b683669`
- 结果版本：`4b6c379846a4b0c42d4d1639f5519664c93dafe5`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40178287662>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；QEMU virtual device；
  无物理硬件

## 结论

Core2 no-stagger 并发已从三实例实际推进到四实例，并在同一时刻达到最大
concurrency `4`。结果不是 PASS：`4×120s` 首批为 `1 PASS / 3 FAIL`。

失败分成两类：

1. attempt 2 完成 WiFi、公网、GATT、PSRAM、frame、QOM 和 pcap 可见工作，
   但仍记录 `hli-errors=1`、`hli-prealloc-failures=2`，health gate 正确
   拒绝；
2. attempt 3/4 在 `UNIFIED_CORE2_READY` 前先出现 NimBLE HCI ACK
   timeout/reset，随后反复 `LoadProhibited @ 0x402630cc`。该地址映射到
   `ble_hs_hci_process_ack()` 的 ACK opcode 读取
   (`ble_hs_hci.c:495`)；reboot 后的 `PC=0` 是次生故障。

因此“四实例及更多实例并发”从 `NOT RUN` 更新为“已执行、开放、FAIL 待修”。
本次同时完成代码/文档权威入口对账，补齐 DOC-01 债务和自动 stale-claim
测试，避免把三实例 PASS 外推成四实例支持。

## 关键证据

- 四实例最大并发：`4`，错峰 `0s`，每 attempt hold `120s`；
- aggregate：`1 PASS / 3 FAIL`；
- attempt 2：`hli-errors=1`、`hli-prealloc-failures=2`；
- attempt 3/4：首个 panic `0x402630cc`，符号化为
  `ble_hs_hci_process_ack()`；
- 平台测试：`465/465 PASS`；
- 文档契约：`36/36 PASS`；
- QEMU profiles：`19/19 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- coverage/catalog/profile/snapshot、Ruff `E9/F`、compileall、
  worker fleet migration 和 `git diff --check`：`PASS`；
- GitHub Actions run `40178287662`：两个 job 均 `PASS`。

firmware SHA-256：
`5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
ELF SHA-256：
`5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
QEMU SHA-256：
`b5b2d878132cb6a8a314cb0f9f9fd0a1843c67fad8558cba268837e9942d304b`。

## 文件

- `report.md`：四实例执行、根因边界、代码/文档整理和验证；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：验证与脱敏摘要；
- `evidence/core2-concurrent-4x120-prealloc-4way-fail.json`：四个 attempt
  的 aggregate evidence，保留原始 PASS/FAIL、HLI health 和 panic 摘要。

结果版本中的源码、文档和 evidence：
[`m5stack-esp-emulator@4b6c379`](https://github.com/m5agent/m5stack-esp-emulator/commit/4b6c379846a4b0c42d4d1639f5519664c93dafe5)。

## 后续修复

- [2026-10-25 expanded HLI reserve](followups/2026-10-25-expanded-hli-reserve/)：
  `0009` 把真实 guest event/ACL reserve 从 `2/2` 扩到 `8/4`；两批独立
  `4×120s` 合计 `8/8 PASS`，Core2 六例外设组 `6/6`、`24/24` checks
  PASS。

本节的 PASS 是独立 follow-up；上面的四实例 `1/4` FAIL 和当时的根因边界
仍保留，不回写成首次即通过。

## 首次记录时未覆盖项

- 四实例修复后的两批独立 aggregate PASS（已由上方 follow-up 覆盖）；
- 五实例及更高并发、持续吞吐和其他 teardown；
- bit-exact Espressif BT controller/baseband；
- 物理板载 PSRAM/cache timing、RF、功耗和电气；
- physical hardware validation。

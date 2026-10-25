# ESP Emulator Core2 HLI ACK observability

- 日期：`2026-10-25`
- 结果：`PARTIAL`（virtual-device validation；根因已收敛，行为修复未完成）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`8c4349cd09a0c2cfd7362830df1825d76615ac9b`
- 结果版本：`3d1484c58ffc4c034bccd2095a47e1e9a2c1a167`
- 运行实现版本：`473e613f99e9a3510c73fe306514749151e745a4`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40188735306>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；QEMU virtual device；
  无物理硬件

## 结论

本轮没有关闭五实例零错峰冷启动。`0010` 只增加由
`M5_CORE2_HCI_PACKET_TRACE=1` 控制的 ACK-state 观测，默认 QEMU 参数和
运行行为保持 `0009` 原路径。

在 `5×20s` 零错峰诊断批中复现 `3 PASS / 2 FAIL`。失败 attempt 中：

- 第一条 HCI Reset 命令已由 Bumble 返回 Command Complete；
- 该 response 却在 `4.506306s` host trace time 后才进入 HLI；
- guest 在首条 HLI 前已经发出三次 Reset，观测到两次 ACK timeout；
- 第一条 event 进入 ACK 检查时 `hci_ack=NULL`、semaphore count `0`；
- HLI 恢复后，旧 Reset Complete 与新 `0x1001` command 交错；
- NimBLE `ble_hs_hci_process_ack` 以 error `12` 调度 reset；
- 后续崩溃在 `0x402630cc` `LoadProhibited`，`PC=0` 是 reset loop 的次生
  故障。

因此当前证据排除了“初始 stale ACK”和“物理 PSRAM/cache 故障”作为首因，
把下一项修复收敛到 HLI response readiness/delivery ordering。

无 trace、单实例 `1/1 PASS` 作为默认路径对照：HLI `45/45`、36
events/9 ACLs、errors/reset/panic 均为 `0`。后续文档/元数据对账明确把
`4.506306s` 标成 host trace time，而不是 guest 虚拟时间，并同步了设备
catalog、QEMU profile 与文档回归测试；运行实现没有因此改变。

## 关键证据

- 零错峰诊断 aggregate：
  `5` requested、`3` PASS、`2` FAIL、maximum concurrency `5`；
- firmware SHA-256：
  `5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
- ELF SHA-256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
- QEMU SHA-256：
  `c1c7e448971c4f189784ff7bba00327a29807c24afd49f65cb4aa0cca2e6e9ce`；
- `0010` patch SHA-256：
  `35656ed4abbbf516ebd984d7aaab5ffc2a17d9df72a223879be24159059184d3`；
- 平台测试：`479/479`；文档契约：`37/37`；Node units：`2/2`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、Ruff `E9/F`、`git diff --check` 和 patch reverse-check：`PASS`。

## 被否决的 workaround

以下实验均未被合入：

- H4 receive 后立即调度 HLI；
- 在 CPU-safe async work 中自观察 pending consumption；
- HLI ready 前阻塞 H2C command；
- 允许上一项未消费时继续多飞行投递。

它们没有形成稳定五实例通过，其中多飞行无 trace 批次为 `0/5`。

## 文件

- `report.md`：完整时间线、实验和验证边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：根因摘要；
- `evidence/evidence-2026-10-25-core2-concurrent-5x20-ack-observability.json`：
  零错峰 aggregate；
- `evidence/evidence-2026-10-25-core2-ack-observability-default-1x.json`：
  默认 trace-off PASS；
- `evidence/evidence-2026-10-25-core2-ack-observability-trace-summary.log`：
  首条 response、ACK-state 和迟到事件顺序；
- `evidence/evidence-2026-10-25-core2-ack-observability-serial-summary.log`：
  timeout、process-ack error 和 panic；
- `evidence/evidence-2026-10-25-core2-ack-observability-peer-summary.log`：
  Bumble H4 命令/响应顺序，动态端口已脱敏；
- `patches/0010-esp32-native-hci-ack-observability.patch`：opt-in 观测 patch。

## 未覆盖项

- 零错峰五实例的行为修复和重复稳定性；
- 大于五实例、持续吞吐和其他 teardown；
- bit-exact Espressif BT controller/baseband；
- 物理 PSRAM/cache timing、RF、功耗和电气；
- physical hardware validation。

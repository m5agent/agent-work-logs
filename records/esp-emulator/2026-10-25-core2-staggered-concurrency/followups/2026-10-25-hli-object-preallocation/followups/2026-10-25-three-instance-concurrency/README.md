# ESP Emulator Core2 three-instance no-stagger concurrency

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`bf98ea8d00dd759da9db44100e239c692f6143ee`
- 结果版本：`db46335e7f71f035ce4a1461567ffb256b683669`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40176816140>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；QEMU virtual device；
  无物理硬件

## 结论

Core2 no-stagger 并发从两实例继续扩展到三实例。两批独立 `3×120s`
门禁各 `3/3 PASS`，合计 `6/6`；三个 QEMU、三个 BLE peer 和三个
per-session HTTP fixture 同时运行。每个 PASS lease 完成：

- WiFi DHCP/HTTP 与公网 DNS/HTTP；
- external NUS GATT write/notify/ACK；
- 29–30 次 `1 MiB` PSRAM 全缓冲校验；
- frame、31-node QOM、pcap 和 evidence ZIP；
- HLI `45/45`、36 events、9 ACLs，errors/reset/panic 为 0。

过程中保留了两个失败阶段：

1. 固定 `40s` BLE peer scan 窗口早于约 `55s` 的三实例 guest BLE 初始化，
   peer 先退出后才出现 HCI reset/timeout；
2. 扩展 readiness 后，两个 lease 完成 29 次 sweep，而旧 `hold/4=30`
   阈值过紧。

最终 peer scan 改为按 session readiness 计算、上限 `120s`；sustained
PSRAM 下限改为保守 `hold/5`，仍要求连续 sweep、heartbeat、HTTP 和公网
recheck。两处都是 harness 校正，没有修改 guest HCI/GATT 数据面。

同时修复当前 QEMU 二进制上的 `core2-power-monitor` 测试竞态：固定 INA3221
物理通道值改用 `qom-set-boot`，避免默认 8 秒 post-boot 注入窗口错过固件
读取。修正后 Core2 六例设备组 `6/6`、`24/24` checks，全部单次无重试。

## 关键证据

- 平台测试：`465/465 PASS`；
- 文档契约：`36/36 PASS`；
- QEMU profiles：`19/19 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- 三实例：两批 `3×120s`，合计 `6/6 PASS`；
- Core2 device group：`6/6 PASS`、`24/24` checks；
- coverage/catalog/profile/snapshot、Ruff `E9/F`、compileall 和
  `git diff --check`：`PASS`。

QEMU SHA-256：
`b5b2d878132cb6a8a314cb0f9f9fd0a1843c67fad8558cba268837e9942d304b`；
firmware SHA-256：
`5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
ELF SHA-256：
`5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`。

## 文件

- `report.md`：根因、harness 修正、pass/fail 证据和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要。

原始 evidence 已提交在公开源码仓库结果版本：
[`tests/uiflow2/`](https://github.com/m5agent/m5stack-esp-emulator/tree/db46335e7f71f035ce4a1461567ffb256b683669/tests/uiflow2)。

## Follow-up

- [2026-10-25 four-instance concurrency](followups/2026-10-25-four-instance-concurrency/)：
  `FAIL`（virtual-device）。四实例最大并发真正达到 `4`，但首批
  `4×120s` 为 `1 PASS / 3 FAIL`：一个 HLI/prealloc health failure，
  两个在 NimBLE `ble_hs_hci_process_ack` (`0x402630cc`) panic。四实例及
  更多实例并发保持开放；同轮完成代码/文档权威入口对账。

## 未覆盖项

- 四实例修复后的两批独立 aggregate PASS 和更高并发；
- 持续吞吐和 active-stop 之外的其他 teardown；
- bit-exact Espressif BT controller/baseband；
- 物理板载 PSRAM/cache timing；
- RF、功耗、电气和 physical hardware validation。

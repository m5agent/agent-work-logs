# ESP Emulator Core2 four-instance expanded HLI reserve

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`4b6c379846a4b0c42d4d1639f5519664c93dafe5`
- 结果版本：`35f5415ede3b635bccf5fac410faab49c0771dbf`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40179581935>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；QEMU virtual device；
  无物理硬件

## 结论

父记录中的四实例 `1 PASS / 3 FAIL` 已由 `0009` 修复。根因不是 Bumble
controller 没有返回 ACK，而是四条 guest 同时冷启动时耗尽了 `0008` 的
2 event/2 ACL 真实 guest 备用对象。`0009` 把 reserve 扩为 8 event/4 ACL，
仍由 guest allocator 分配真实 transport 对象，没有合成 ACK，也没有绕过
HLI 或 Device Service。

两批独立 `4×120s`、零错峰运行各 `4/4 PASS`，合计 `8/8 PASS`。每个
lease 均完成 WiFi、公网、BLE NUS GATT、PSRAM 全缓冲校验、frame/QOM、
pcap、evidence 和 cleanup；结束时 QOM event/ACL reserve depth 为 `8/4`，
HLI `45/45`、36 events/9 ACLs，`hli-errors=0`，无 scheduler reset 或
panic。首批一个 lease 记录 2 次可恢复的 refill failure，后补满并完成全部
门禁；确认批为 0。

## 关键证据

- 四实例最大并发：`4`，startup stagger `0s`，每 attempt hold `120s`；
- 两批 aggregate：`4/4 PASS`、`4/4 PASS`，合计 `8/8`；
- 每 lease HLI：`45/45`，HLI errors/reset/panic 均为 0；
- guest transport：36 events、9 ACLs 全走 fast path，结束 depth `8/4`；
- `0009` 源码构建的 Core2 六例外设组：`6/6` case、`24/24` checks，
  全部单次、无 retry；
- 平台契约与 CI：本记录不重写父记录的历史失败，修复 PASS 作为独立
  follow-up 保存。

firmware SHA-256：
`5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
ELF SHA-256：
`5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
并发 PASS QEMU SHA-256：
`139195d974fc23594c2508becd7d9a351315164f8b91d72e9793e8fa25a65e96`；
`0009` 设备组 QEMU SHA-256：
`0e1165fb866ecb573cdaca2084bdf498b45432aaa1937674ca73d04eeaa7a7fc`。

## 文件

- `report.md`：根因、修复、执行和验证边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏后的聚合摘要；
- `evidence/core2-concurrent-4x120-prealloc8x4-pass-a.json`：首批四实例；
- `evidence/core2-concurrent-4x120-prealloc8x4-confirm-pass-b.json`：
  独立确认批；
- `evidence/core2-0009-device-group.json`：`0009` 源码构建的 Core2
  六例外设组；
- `patches/0009-esp32-native-hci-expand-hli-preallocation.patch`：最小修复。

## 未覆盖项

- 五实例及更高并发；
- 持续吞吐和其他 teardown 模式；
- bit-exact Espressif BT controller/baseband；
- 物理板载 PSRAM/cache timing；
- RF、功耗、电气和 physical hardware validation。

# ESP Emulator Core2 post-reset teardown

- 日期：`2026-10-29`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 问题来源：[PR #25](https://github.com/m5agent/m5stack-esp-emulator/pull/25) / `CORE2-02`
- Base：`d31da27e8c4677e197ff1363f63e82043f651577`
- 实现提交：`86454588beef9180f207dc4eafd52acfe764b4f4`
- 合并提交：`741005a93e16950292ceba24c06fd5062d00e2b5`
- 环境：macOS arm64；Device Service `/api/v1`；`core2-native-hci`；`qemu-unified`

## 结论

teardown runner 新增 `active|after-reset` 两种停止模式，并保持 `active` 为
兼容默认值。`after-reset` 会先捕获 full-ready 状态下的 frame、QOM、network、
external NUS GATT、pcap 和 evidence，再向 guest 注入 `system_reset`；确认
session 与同一 QEMU PID 在 reboot-in-flight 时仍存活后，停止 session 并验证
HTTP/BLE companion、BLE/QEMU PID 和 worker lease 全部回收。连续三个 lease
均通过全部 `23/23` checks，下一轮也能正常创建新 session。

## 关键证据

- firmware SHA256：
  `c3eaa35b9c41204cc6337e30b1d81f60bf06eab2d747f3547af5d8b8ba0ea99f`
- matching ELF SHA256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`
- QEMU SHA256：
  `54e7a7f7cd0ff6f5a1d6343c06563388f49c2b0abbca4cafb850876e57ed1254`
- teardown runner SHA256：
  `586a8195db5a61c8ace06ad4fe07b95b371cab6915dcc5cfaaf38720145c2395`
- 原始 machine evidence SHA256：
  `ea540bdac28249c2a52578d8e582a17885886ee0f6db9009a43c788a61234fb6`
- 每轮 native-HCI health `45/45`；36 events / 9 ACLs；HLI
  error/reset/panic/queue depth 均为 `0`
- 平台回归：`1535 OK + 10 skipped`
- PR CI 双 job 与合并后 main CI `40837477524`：PASS

源码证据：

- [teardown 结果说明](https://github.com/m5agent/m5stack-esp-emulator/blob/741005a93e16950292ceba24c06fd5062d00e2b5/docs/evidence/2026-10-29-core2-post-reset-teardown/README.md)
- [machine evidence](https://github.com/m5agent/m5stack-esp-emulator/blob/741005a93e16950292ceba24c06fd5062d00e2b5/tests/uiflow2/core2_native_hci/evidence-2026-10-29-core2-post-reset-stop-recovery-3x.json)

## 文件

- `report.md`：实现、执行、验证层级与回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary

## 未覆盖项

- physical hardware 与 RF/电气测量；
- bit-exact Espressif BT controller/baseband；
- 物理板载 PSRAM/cache timing 与性能；
- 大于当前服务容量、持续吞吐及 active-stop/post-reset 之外的 teardown；
- cross-host QEMU migration、guest 内部完全 quiesce 和恶意固件沙箱。

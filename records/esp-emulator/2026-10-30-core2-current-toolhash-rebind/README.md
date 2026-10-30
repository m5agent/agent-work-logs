# M5Stack ESP Emulator Core2 current tool-hash rebind

- 日期：`2026-10-30`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 问题来源：`CORE2-02` 当前 main 工具哈希回归
- 源码版本：`m5stack-esp-emulator @ 4af1e9f5cdc3cbfcd1fca7d11fd707454c36f357`
- 基线与验证对象：`origin/main @ 3fc436e4aa99176ef3a4f7a2d35d25c973659219`
- 交付：源码提交已创建；PR 指引本记录，合并 SHA 在交付后回填
- 环境：macOS arm64、Python 3.12、Device Service `/api/v1`、QEMU unified Core2

## 结论

SVC-03 的三个无语义 boundary move 改变了 `device_service.py` 的工具哈希。
在最新 main 上重新运行两批独立零错峰 `2x60s` 后，全部 `4/4 PASS`，说明这次
拆分没有改变本回归覆盖的 Device Service、QEMU runtime、WiFi、BLE、
PSRAM、frame/QOM、pcap、evidence 和清理行为。

每个 lease 都完成三次 1 MiB PSRAM sweep、两次受控 HTTP/公网重检、WiFi
DHCP/HTTP、公网 DNS/HTTP、外部 NUS GATT、非空 frame、32 节点 QOM、
pcap、evidence ZIP 和 cleanup。每 lease 的 HLI 为 `45/45`、36 fast-path
events、9 ACLs；errors、preallocation failures、panic、drops、GATT timeout、
session read error 和 cleanup error 均为 `0`。输入资产在首个 lease 前冻结，
运行期间没有漂移。

## 关键证据

- Original/service firmware：
  `ae094f4824d15499a5770018393660d1051866743dec52265552b6fc23eb2a23`
- ELF：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`
- QEMU：
  `54e7a7f7cd0ff6f5a1d6343c06563388f49c2b0abbca4cafb850876e57ed1254`
- Previous `device_service.py`：
  `5b4ed0f576dae7a23151049f753acdfd6bf1ddce2d44e3c3389413b2b6349acb`
- Current `device_service.py`：
  `a96b15061d104aa79e7af74b513e5881481acf62a847d5ba1e27c5997aa1bbbb`
- Batch A raw evidence SHA256：
  `c0e4ad6d7fe3c4d07c922c0cb7df2072baaf058fa774f00dd72f4e213bed935a`
- Batch B raw evidence SHA256：
  `4409b748203c6ab4ddcc1c2b70c639fce7c8f7c85047f6ad58a8bbf0b8813dce`
- Platform full suite：`1,678` tests，`1,677 PASS + 1 skip`
- Runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`
- Source PR scope、JSON、UTF-8 与 `git diff --check`：`PASS`

源码固定链接：

- <https://github.com/m5agent/m5stack-esp-emulator/blob/4af1e9f5cdc3cbfcd1fca7d11fd707454c36f357/docs/evidence/2026-10-30-core2-toolhash-rebind/README.md>
- <https://github.com/m5agent/m5stack-esp-emulator/blob/4af1e9f5cdc3cbfcd1fca7d11fd707454c36f357/docs/evidence/2026-10-30-core2-toolhash-rebind/summary.json>

## 文件

- `report.md`：触发原因、执行参数、证据、边界和回滚
- `run.json`：机器可读结果
- `evidence/summary.json`：脱敏聚合证据与工具哈希
- `patches/`：不适用；改动是源码/文档提交
- `code/`：不适用；runner 位于主仓库

## 未覆盖项

- 当前宿主负载下的八实例 cold-start tool-hash 重绑仍为 `NOT RUN`；
- 九实例容量仍被拒绝，`ble_hs_hci_process_ack` 竞态未修复；
- 持续吞吐和更复杂 teardown 未重跑；
- bit-exact Bluetooth controller/baseband、RF、电气、物理 PSRAM/cache
  timing 和真机验证均为 `NOT RUN`。

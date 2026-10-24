# ESP Emulator Core2 同 guest BLE 重连修复：2 到 30 轮

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 首次修复版本：`m5agent/m5stack-esp-emulator @ b59605fcfaa5d6b319c8bef22fc02f7eee0bcb1f`
- 五轮 follow-up 与文档基线：`m5agent/m5stack-esp-emulator @ 6956ebbe2c620c5840e04da8911a554fee7d7491`
- 十轮 follow-up 与 timeout 修复：`m5agent/m5stack-esp-emulator @ e9520bbca56da753cd4cd75cf30c8c5594866386`
- 二十轮 follow-up：`m5agent/m5stack-esp-emulator @ 36e28d76b3c293975878d1980dbd5349d1a9efe4`
- 三十轮 follow-up：`m5agent/m5stack-esp-emulator @ c2545835091a6fb321c73a517fe66655c8160686`
- 基线版本：`e686838e38dc8ec46daa6dbc2830322806ca7355`
- 环境：macOS Apple Silicon；Python 3；patched QEMU；UIFlow2 v2.5.3 Core2 和匹配 ELF

## 结论

同一 Core2 guest 的两轮 BLE NUS GATT 已修复并通过 3 个独立 Device Service
lease。第二轮不再只看 advertisement：外部 peer 重新 scan/connect、发现和
订阅 NUS、写入 payload，并收到 guest 的 `ACK:M5_CORE2_UNIFIED`。

根因不在固件 NimBLE、QEMU HLI 或连接池。外部 Bumble compatibility 层错误地
为无响应的 `HCI_Host_Number_of_Completed_Packets (0x0c35)` 发送了
Command Status。该 stale ACK 被下一条 `LE Set Advertising Data (0x2008)`
消费，`ble_hs_hci_process_ack` 因 opcode mismatch 返回
`BLE_HS_ECONTROLLER (12)` 并触发 NimBLE reset loop。

修复后 3/3 个 lease 都满足：

- 每轮 HLI 73 posts / 73 consumed，HLI 和 meta queue 为空；
- `trace-hs-sched-reset=0`；
- `trace-gap-adv-start=2`；
- 第二轮 guest RX、notification、pcap 和 evidence 全部 PASS；
- frame/QOM、WiFi、公网 DNS/HTTP 同时保持 PASS。

## 五轮 follow-up

同一 peer-process 路径随后从每个 lease 两轮扩大到五轮。3 个独立 Device
Service lease 各自完成 5 轮 scan/connect/NUS GATT/disconnect，`3/3 PASS`。
每个 lease 均为 HLI `157/157`、events `112`、ACLs `45`，HLI errors 和
HLI/meta queue 深度为 0；connection/L2CAP/GATT 池回到 `3/9/3` 空闲基线，
`trace-hs-sched-reset=0`、`trace-gap-adv-start=5`。同一固件 SHA、ELF 和
QEMU 二进制继续与初始两轮证据保持一致。

## 十轮 follow-up

同一路径进一步扩大到当前 session API 上限：3 个独立 Device Service lease
各自完成 10 轮 scan/connect/NUS GATT/disconnect，`3/3 PASS`。每个 attempt
的 peer `CYCLE_PASS`、guest RX 和 guest ACK marker 都精确为 10。

每个 lease 均为 HLI `297/297`、events `207`、ACLs `90`，HLI errors 和
HLI/meta queue 深度为 0；connection/L2CAP/GATT 池回到 `3/9/3`，
`trace-hs-sched-reset=0`、`trace-gap-adv-start=10`。frame/QOM、WiFi、
公网 DNS/HTTP、pcap 和 evidence ZIP 同时 PASS。

第一次十轮运行暴露了独立的 Device Service 缺陷：peer 已完成 5 轮并开始
第 6 轮，guest 没有 panic，但 `_wait_hci_probe_result()` 把 configured
ready timeout 硬截断为 30 秒，误判失败并终止 QEMU。失败 evidence 被保留；
等待现在使用 session ready timeout，并新增超过 30 秒仍可完成的回归测试。

## 二十轮 follow-up

Device Service、Bumble peer 和 service runner 原先各自硬编码
`ble_reconnect_cycles=1..10`。本轮统一扩展到 `1..30`，并增加 20 轮接受、
31 轮拒绝的契约回归。

使用重新构建的 unified Core2 镜像、同一 ELF 和同一 QEMU SHA，3 个独立
Device Service lease 各自完成 20 轮 scan/connect/NUS GATT/disconnect，
`3/3 PASS`。每个 attempt：

- peer `BLE_BUMBLE_CYCLE_PASS`、guest RX 和 ACK marker 均为 20；
- HLI `577/577`，events `397`，ACLs `180`；
- `hli-errors=0`，HLI/meta queue 深度为 0；
- connection/L2CAP/GATT 池回到 `3/9/3`；
- `trace-hs-sched-reset=0`、`trace-gap-adv-start=20`；
- frame/QOM、WiFi、公网 DNS/HTTP、pcap 和 evidence ZIP 全部 PASS；
- 无 panic、无 dropped packet。

## 三十轮 follow-up

使用同一 unified Core2 镜像 SHA、ELF SHA 和 QEMU SHA，3 个独立 Device
Service lease 各自完成 30 轮 scan/connect/NUS GATT/disconnect，`3/3 PASS`。
每个 attempt：

- peer `BLE_BUMBLE_CYCLE_PASS`、guest RX 和 ACK marker 均为 30；
- HLI `857/857`，events `587`，ACLs `270`；
- `hli-errors=0`，HLI/meta/TX queue 深度为 0；
- connection/L2CAP/GATT 池回到 `3/9/3`；
- `trace-hs-sched-reset=0`、`trace-gap-adv-start=30`；
- frame/QOM、WiFi、公网 DNS/HTTP、pcap 和 evidence ZIP 全部 PASS；
- 无 panic、无 dropped packet。

## 关键证据

- 平台测试：初始修复 `300/300 PASS`，十轮 follow-up `301/301 PASS`；
- Node：`2/2 PASS`；
- GitHub Actions CI run `40068768706`（首次修复）：`PASS`；
- GitHub Actions CI run `40069447311`（五轮 follow-up 与文档收口）：`PASS`；
- GitHub Actions CI run `40070310548`（十轮 follow-up）：`PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- QEMU observability patch 正向 replay check 和当前 worktree reverse check：
  `PASS`；
- 同 guest 双轮 reconnect：3 个独立 lease `3/3 PASS`；
- 同 guest 五轮 reconnect：3 个独立 lease `3/3 PASS`；
- 同 guest 十轮 reconnect：3 个独立 lease `3/3 PASS`；
- 同 guest 二十轮 reconnect：3 个独立 lease `3/3 PASS`；
- 同 guest 三十轮 reconnect：3 个独立 lease `3/3 PASS`；
- 二十轮 follow-up：平台测试 `314/314 PASS`，Node `2/2 PASS`，CI run
  `40074452179` 两个 job 均 `PASS`；
- 三十轮 follow-up：平台测试 `318/318 PASS`，Node `2/2 PASS`，CI run
  `40079740981` 两个 job 均 `PASS`；
- 完整 67-case UIFlow2 外设矩阵本轮未重跑：`NOT RUN`；
- 物理硬件、RF、bit-exact BT baseband/controller：`NOT RUN`。

## 文件

- `report.md`：根因、修复、执行和边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：聚合验证和 artifact hash
- `evidence/verification.reconnect5.summary.json`：五轮 follow-up 的独立证据摘要
- `evidence/verification.reconnect10.summary.json`：十轮 follow-up、等待修复和失败历史的独立证据摘要
- `evidence/verification.reconnect20.summary.json`：二十轮 follow-up、API 上限扩展和逐 lease health 摘要
- `evidence/verification.reconnect30.summary.json`：三十轮 follow-up 和逐 lease health 摘要

## 未覆盖项

- 未执行超过 30 轮连续重连或多小时 soak；
- 未验证 pairing/security/encrypted reconnect；
- 未验证 bit-exact Espressif BT controller/baseband；
- 未执行物理 cache/PSRAM 等价性或真机同路径验证；
- 未重跑完整 UIFlow2 外设矩阵。

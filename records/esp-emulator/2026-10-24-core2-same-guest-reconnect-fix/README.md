# ESP Emulator Core2 同 guest BLE 重连修复

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ b59605fcfaa5d6b319c8bef22fc02f7eee0bcb1f`
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

## 关键证据

- 平台测试：`300/300 PASS`；
- Node：`2/2 PASS`；
- GitHub Actions CI run `40068768706`：`PASS`；
- runtime coverage、peripheral catalog、QEMU profiles：`PASS`；
- QEMU observability patch 正向 replay check 和当前 worktree reverse check：
  `PASS`；
- 同 guest 双轮 reconnect：3 个独立 lease `3/3 PASS`；
- 完整 67-case UIFlow2 外设矩阵本轮未重跑：`NOT RUN`；
- 物理硬件、RF、bit-exact BT baseband/controller：`NOT RUN`。

## 文件

- `report.md`：根因、修复、执行和边界
- `run.json`：机器可读记录
- `evidence/verification.summary.json`：聚合验证和 artifact hash

## 未覆盖项

- 未执行 5 轮以上连续重连或多小时 soak；
- 未验证 pairing/security/encrypted reconnect；
- 未验证 bit-exact Espressif BT controller/baseband；
- 未执行物理 cache/PSRAM 等价性或真机同路径验证；
- 未重跑完整 UIFlow2 外设矩阵。

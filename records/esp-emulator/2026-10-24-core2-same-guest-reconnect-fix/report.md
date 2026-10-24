# ESP Emulator Core2 同 guest BLE 重连修复报告

## 背景

Core2 首轮 BLE GATT 和两分钟 active-link hold 已通过，但 peer 断开后第二轮
连接失败。失败时出现重复 `NimBLE: HCI process ack returned 12`，随后 HCI
reset，第二轮没有 advertisement。

目标是在同一个 guest、同一个 Device Service lease 中完成至少两轮完整
scan/connect/NUS GATT/disconnect，并保留 serial、peer、pcap、QOM 和
evidence。

## 根因

逐步排除：

- 真正不重新广告的对照可以完成第一轮且不会 reset，说明 disconnect 本身正常；
- QEMU HLI packet trace 显示 disconnect event 有序交付；
- conn/L2CAP/GATT pool 分别保持 `3/9/3` 个空闲槽，没有资源泄漏；
- `ble_hs_sched_reset` 在下一轮 `hci_cmd_tx(0x2008)` 后触发；
- Bumble peer trace 显示 `HCI_Host_Number_of_Completed_Packets (0x0c35)`
  被错误回复了 Command Status；
- 下一条 `LE Set Advertising Data` 的等待被这个 stale ACK 提前唤醒，
  opcode mismatch 返回 `BLE_HS_ECONTROLLER (12)`。

Bluetooth Core Vol 4, Part E, 7.3.35 规定该命令没有 Command Complete 或
Command Status 响应。

## 修复

- `platform/tools/ble_probe.py` 的 Bumble compatibility handler 对 `0x0c35`
  返回 `None`，不发送任何 HCI event；
- 增加 `platform/tests/test_ble_probe.py`，防止重新引入非法响应；
- 增加 `0006-esp32-native-hci-observability.patch`，提供 opt-in H4 packet
  trace、HCI command/reset/advertising counters、HLI deferred counters 和
  connection/L2CAP/GATT pool counters；
- 更新当前状态、Backlog、Core2 设计、validation ledger 和测试文档。

## 执行

```bash
ninja -C "$QEMU_ROOT/build/qemu/build" qemu-system-xtensa

PYTHONPATH=.work/py:platform/tools \
python3 tests/uiflow2/core2_native_hci/run_service_5x.py \
  --base-url "$DEVICE_SERVICE" \
  --image "$CORE2_IMAGE" \
  --elf "$CORE2_ELF" \
  --qemu "$QEMU_ROOT/build/qemu/build/qemu-system-xtensa" \
  --attempts 3 \
  --ble-reconnect-cycles 2 \
  --out-dir "$EVIDENCE_DIR"
```

QEMU packet trace 通过 `M5_CORE2_HCI_PACKET_TRACE=1` 选择。
GitHub Actions CI run `40068768706` 的 platform-contracts 和
network-namespace-policy 两个 job 均通过。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU rebuild、`compileall`、定向 Ruff |
| transport | `PASS` | 两轮 H2C/C2H、H4 packet trace 和 Bumble peer log |
| device_response | `PASS` | 第二轮 NUS discovery、subscribe、write 和 guest RX |
| data_behavior | `PASS` | 第二轮 notification `ACK:M5_CORE2_UNIFIED` |
| visual | `PASS` | 3/3 frame SHA 一致且 frame 非空；UI 不属于本修复 |
| hardware | `NOT RUN` | 全部为 virtual-device validation |

## 关键 artifact

- Firmware SHA256：
  `b9c91c40e60867186717938e075da8b19271cc8e7a22323524be213beff81982`
- ELF SHA256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`
- QEMU SHA256：
  `e65c6f5cad2ee2c11efb1cf13ce81639c53666ac22c708fb81501cfb689614c1`
- QEMU observability patch SHA256：
  `c784e7c36459147aafc30c92e138d34a2921d51b3d69749a345f24714b4214c6`
- reconnect evidence SHA256：
  `d0aefdaf1688ea2fe8512737258cef1314fc9e4175af37336bfdde04089371b5`

## 验证边界

- 首次修复验证两轮；后续 follow-up 已扩大到每个 lease 五轮；
- 未证明配对、安全连接或加密重连；
- 未证明 bit-exact Espressif BT controller/baseband；
- 未证明物理 cache/PSRAM 时序、RF、吞吐或硬件行为；
- 完整 67-case 外设矩阵本轮未重跑。

## 风险与回滚

回滚可整体 revert `b59605fcfaa5d6b319c8bef22fc02f7eee0bcb1f`。
QEMU observability 默认关闭，只在显式环境变量下输出 packet trace，不改变
GATT 数据面。未操作物理设备。

## Follow-up：五轮重连与文档收口

源码收口版本：
`m5agent/m5stack-esp-emulator @ 6956ebbe2c620c5840e04da8911a554fee7d7491`。

同一固件、ELF 和 QEMU build 在 3 个独立 Device Service lease 中各自完成
5 轮 scan/connect/NUS GATT/disconnect：

- 每轮都保留 frame/QOM、WiFi、公网 DNS/HTTP、外部 NUS GATT、pcap 和
  evidence；
- 每个 lease 的 HLI posts/consumed 为 `157/157`，events `112`，ACLs `45`；
- `hli-errors=0`，HLI/meta queue 深度为 0；
- connection/L2CAP/GATT 池为 `3/9/3`，没有连接资源泄漏；
- `trace-hs-sched-reset=0`、`trace-gap-adv-start=5`；
- 外部 Bumble peer 在五轮中均重新发现、连接、写入并收到 notification。

同时重新核对 README、项目状态、Backlog、工作流台账、设备矩阵、统一运行时
契约、Device Service API、Core2 设计页、验证台账和 QEMU profile，使当前
结论统一为五轮 PASS，并将双轮证据保留为较早里程碑。

本 follow-up 的验证：

- 平台套件 `300/300 PASS`；
- Node `2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall 和定向
  Ruff：`PASS`；
- GitHub Actions CI run `40069447311`：两个 job 均 `PASS`；
- QEMU `0006` patch reverse-check：`PASS`；
- QEMU SHA256 与五轮 evidence 记录一致。

以下仍未执行：超过五轮重连、多小时 coexistence/soak、配对/安全/加密重连、
bit-exact ESP32 BT controller/baseband、物理 cache/PSRAM 和真机。

## Follow-up：十轮重连与 Device Service 等待修复

源码收口版本：
`m5agent/m5stack-esp-emulator @ e9520bbca56da753cd4cd75cf30c8c5594866386`。

同一固件、ELF 和 QEMU build 在 3 个独立 Device Service lease 中各自完成
10 轮 scan/connect/NUS GATT/disconnect：

- 每个 attempt 的 peer `BLE_BUMBLE_CYCLE_PASS`、guest
  `UNIFIED_CORE2_BLE_RX` 和 `UNIFIED_CORE2_BLE_ACK_SENT` 都精确为 10；
- 每个 lease 的 HLI posts/consumed 为 `297/297`，events `207`，ACLs `90`；
- `hli-errors=0`，HLI/meta queue 深度为 0；
- connection/L2CAP/GATT 池为 `3/9/3`，没有连接资源泄漏；
- `trace-hs-sched-reset=0`、`trace-gap-adv-start=10`；
- frame/QOM、WiFi、公网 DNS/HTTP、pcap 和 evidence ZIP 全部 PASS。

第一次十轮运行没有到达 guest panic：peer 已完成 5 轮并开始第 6 轮，但
`DeviceSession._wait_hci_probe_result()` 将 session ready timeout 硬截断
为 30 秒，导致 Device Service 判定 peer 未完成、终止 QEMU。修复后等待
直接受 session ready timeout 限制，并增加
`test_hci_probe_wait_allows_multi_cycle_completion_after_30_seconds`
防止回归。

本 follow-up 的验证：

- 平台套件 `301/301 PASS`；
- Node `2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall 和定向
  syntax Ruff：`PASS`；
- GitHub Actions CI run `40070310548`：两个 job 均 `PASS`；
- 10 轮 PASS evidence、首次 10 轮 timeout failure 和所有历史 milestone
  均独立保留。

以下仍未执行：超过当前 1–10 API 上限的重连、多小时 coexistence/soak、
配对/安全/加密重连、bit-exact ESP32 BT controller/baseband、物理
cache/PSRAM 和真机。

## Follow-up：二十轮重连与 API 上限扩展

源码收口版本：
`m5agent/m5stack-esp-emulator @ 36e28d76b3c293975878d1980dbd5349d1a9efe4`。

变更：

- `platform/tools/device_service.py`：`ble_reconnect_cycles` 从 `1..10`
  扩到 `1..30`；
- `platform/tools/ble_probe.py`：Bumble peer 的
  `--reconnect-cycles` 同步扩到 `1..30`；
- `tests/uiflow2/core2_native_hci/run_service_5x.py`：服务测试 runner 同步；
- `test_device_service.py` 增加 20 接受、31 拒绝的契约断言；
- `test_docs_consistency.py` 固定 3 attempts × 20 cycles、HLI 577/577、
  events 397、ACLs 180、池 `3/9/3` 和 `trace-gap-adv-start=20`。

本轮使用重新构建的 unified Core2 镜像：

- firmware SHA256：
  `4e1012c419d04e7188bb8c45476f6f5eb4d509f227bc4e385a805ce011916e02`；
- ELF SHA256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
- QEMU SHA256：
  `e65c6f5cad2ee2c11efb1cf13ce81639c53666ac22c708fb81501cfb689614c1`。

ELF 和 QEMU 与十轮证据一致；unified 镜像由同一 UIFlow2 build 和 LittleFS
重新 compose，产物 SHA 因此单列，不能沿用旧镜像 hash。

执行 3 个独立 `/api/v1` lease，每个要求 20 轮。结果 `3/3 PASS`：

- 每个 attempt 的 peer、guest RX 和 ACK marker 均为 20；
- HLI posts/consumed 均为 `577/577`；
- events 397、ACLs 180；
- `hli-errors=0`、HLI/meta queue 和 TX/RX 异常队列为零；
- connection/L2CAP/GATT 池均回到 `3/9/3`；
- `trace-hs-sched-reset=0`、`trace-gap-adv-start=20`；
- frame/QOM、WiFi/公网、pcap、evidence 和 manifest binding 全部 PASS；
- 无 panic。

验证：

- 平台套件 `314/314 PASS`；
- Node `2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall 和定向
  Ruff：`PASS`；
- GitHub Actions CI run `40074452179`：两个 job 均 `PASS`；
- 完整 UIFlow2 67-case 外设矩阵本轮未重跑。

边界：

- virtual-device validation，不是物理 RF、功耗或硬件；
- 20 轮短时 reconnect 不等于多小时 coexistence/soak；
- 未证明 pairing、secure connection、encrypted reconnect；
- 未证明 bit-exact BT controller/baseband；
- 未证明物理 cache/PSRAM 时序。

回滚：revert
`36e28d76b3c293975878d1980dbd5349d1a9efe4`。回滚后 API 恢复 `1..10`
限制，但已提交的二十轮证据仍保留为历史。

## Follow-up：三十轮重连

源码收口版本：
`m5agent/m5stack-esp-emulator @ c2545835091a6fb321c73a517fe66655c8160686`。

使用与二十轮 follow-up 相同的 unified Core2 镜像、ELF 和 QEMU SHA，运行
3 个独立 `/api/v1` lease，每个要求 30 轮：

- 每个 attempt 的 peer、guest RX 和 ACK marker 均为 30；
- HLI posts/consumed 均为 `857/857`；
- events 587、ACLs 270；
- `hli-errors=0`，HLI/meta/TX queue 深度为 0；
- connection/L2CAP/GATT 池均回到 `3/9/3`；
- `trace-hs-sched-reset=0`、`trace-gap-adv-start=30`；
- frame/QOM、WiFi/公网、pcap、evidence 和 manifest binding 全部 PASS；
- 无 panic、无 dropped packet。

验证：

- 平台套件 `318/318 PASS`；
- Node `2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall：
  `PASS`；
- GitHub Actions CI run `40079740981`：两个 job 均 `PASS`；
- 完整 UIFlow2 67-case 外设矩阵本轮未重跑。

边界：

- virtual-device validation，不是物理 RF、功耗或硬件；
- 30 轮短时 reconnect 不等于超过三十轮或多小时 coexistence/soak；
- 未证明 pairing、secure connection、encrypted reconnect；
- 未证明 bit-exact BT controller/baseband；
- 未证明物理 cache/PSRAM 时序。

回滚：revert
`c2545835091a6fb321c73a517fe66655c8160686`。三十轮 evidence 将回退，
源码运行路径不变。

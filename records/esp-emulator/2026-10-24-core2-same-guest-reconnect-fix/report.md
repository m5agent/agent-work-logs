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

- 只验证两轮；更多连接轮次仍属于 Backlog；
- 未证明配对、安全连接或加密重连；
- 未证明 bit-exact Espressif BT controller/baseband；
- 未证明物理 cache/PSRAM 时序、RF、吞吐或硬件行为；
- 完整 67-case 外设矩阵本轮未重跑。

## 风险与回滚

回滚可整体 revert `b59605fcfaa5d6b319c8bef22fc02f7eee0bcb1f`。
QEMU observability 默认关闭，只在显式环境变量下输出 packet trace，不改变
GATT 数据面。未操作物理设备。

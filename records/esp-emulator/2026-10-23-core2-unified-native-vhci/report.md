# Core2 unified WiFi + stock native-VHCI BLE 报告

## 背景

此前 stock Core2 native-VHCI BLE 只在一个独立 BLE runner 中通过。另一个
unified runner 使用 HCI-UART 测试构建，不能证明 stock firmware 的内置
controller 路径可以和板级、WiFi 在同一个 guest 中共同运行。

## 阻塞和修复

第一次合并时 WiFi 通过，但进入 BLE coexist 后稳定崩溃在：

```text
coex_force_wifi_mode
→ force_wifi_mode
→ phy_force_wifi_chan
→ esp_dport_access_reg_read
```

classic ESP32 BB idle 页 `0x3ff5d000` 由 QEMU 的 unimp-default 区域返回
全 1。`phy_force_wifi_chan()` 因此持续看到 hardware-busy 位。新增 patch
`0002-classic-esp32-bb-idle-readback.patch`，将该 idle 页改为默认读 0。

随后出现 GDB software breakpoint 残留导致的 `BREAK instr`。处理方式是在
guest callback 注入时临时禁用所有 bridge breakpoint，注入完成后恢复，避免
inferior call 期间 nested breakpoint 破坏 guest 代码。

## 实现

- `unified_core2/run_test.py` 新增 `--ble-transport native-vhci`；
- 复用原 unified runner 的 frame、touch、QOM、音频、HTTP 和公网测试；
- native transport 使用 QEMU GDB bridge 接管 stock VHCI；
- 新增 `--require-all-attempts`，防止仅一次 PASS 后提前结束；
- 新增 sanitized evidence：`evidence-2026-10-23-native-vhci.json`。

## 验证

```text
attempt 1 PASS
attempt 2 PASS
attempt 3 PASS
```

每次均命中：

- display 320x240、touch redraw、QOM power/INA/IMU；
- speaker/microphone PCM；
- WiFi DHCP lease；
- controlled HTTP `/unified`；
- public DNS 和 public IPv4 HTTP；
- external peer found/connect/GATT/subscription/write/notify；
- bridge H2C/C2H event 和 ACL；
- guest RX/ACK marker。

## 边界

本次是 virtual-device validation。GDB bridge 仍是诊断实现，未进入 Device
Service 的单 lease 状态机和 evidence ZIP。RF、功耗、声学、光学、机械、
bit-exact BT controller 和真机验证仍不在此 PASS 范围内。

## 回滚

回滚源码提交 `7823befc2cee622e6b086287f5ae903fda839885` 可撤销 unified
native transport、BB idle patch、
runner 选项和文档更新；没有修改物理设备。

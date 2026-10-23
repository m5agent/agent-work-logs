# ESP Emulator Core2 stock native-VHCI BLE GATT 报告

## 背景

Core2 已有两条 BLE 路径：QEMU 中的 stock UIFlow2 能启用内置 controller 并
返回 `gap_advertise()`，但没有外部 peer 能观察到广播；另有 HCI-UART 测试构建
通过 UART1 把 NimBLE H4 交给 Bumble，可以完成 GATT，但需要替换固件的 HCI
transport。

因此“advertising-enable PASS”和“HCI-offload GATT PASS”都不能证明 stock
固件自己的 controller 路径能够完成外部连接与 GATT。

## 根因和方案

QEMU 的 Core2 BT bootstrap 只提供 BT RAM、controller 身份和初始化寄存器，
没有 baseband connection 或 ACL 数据面。HCI-UART 路径则完全绕开内置 controller。

固件 ELF 保留了完整的 VHCI 符号：

- `API_vhci_host_send_packet`
- `esp_vhci_host_register_callback`
- `vhci_env_p`
- firmware 注册的 `notify_host_recv`
- controller 侧 `vhci_send`

新方案在 QEMU GDB 中：

1. 在 `API_vhci_host_send_packet` 读取 stock firmware 发出的 H2C；
2. `return` 掉未实现的 in-guest controller 调用；
3. 把原始 H4 字节转给 Bumble controller；
4. 从 Bumble 读取 C2H；
5. 用 firmware 自己注册的 callback 注入 event/ACL；
6. 在 idle 点等待异步 connection/ACL event，再恢复 guest。

实现：

- `platform/tools/hci_stream.py`：H4 command/event/ACL 分包；
- `tests/uiflow2/core2_radio_probe/native_vhci_bridge.py`：GDB 注入和回调；
- `tests/uiflow2/core2_native_vhci/run_test.py`：自动启动 QEMU、GDB bridge、
  Bumble controller/peer，生成 evidence。

## 验证

```text
native-VHCI GATT       5/5 PASS
platform tests         213/213 PASS
Core2 peripheral       6/6 PASS
Core2 frame/input      1/1 PASS
runtime coverage       RUNTIME_COVERAGE_OK
peripheral catalog     PERIPHERAL_CATALOG_OK
QEMU profiles          QEMU_PROFILES_OK
```

每次 PASS 均要求：

- guest：`CORE2_HCI_BLE_RX`、`CORE2_HCI_BLE_ACK_SENT`；
- peer：found、connected、GATT discovered、subscribed、write、
  notification OK、PASS；
- bridge：H2C、C2H、ACL H2C、ACL C2H；
- firmware copy 在运行前后 SHA256 不变。

## 边界

- 当前 bridge 是 GDB 诊断实现，不是最终服务组件；
- 没有进入 Device Service 的单 lease unified 会话；
- Bumble 代替 Espressif controller 执行 controller 侧语义，没有运行
  bit-exact baseband/controller；
- 不证明 RF、距离、共存、配对/安全、吞吐或功耗；
- 所有结果均为 virtual-device validation，物理硬件 `NOT RUN`。

## 回滚

源码提交为
`1546798de9db5df52e3045527281c2a8d01dcc4d`。回滚该提交可撤销 native-VHCI
runner、bridge、H4 parser、测试和文档更新；没有修改或擦除物理设备。

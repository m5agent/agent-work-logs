# ESP Emulator Core2 native HCI transport 报告

## 背景

Core2 stock UIFlow2 的 native-VHCI BLE 目前由 QEMU GDB bridge 完成。
同 commit Device Service repeated lease 为 `1/2`，失败来自 H2C sender
context 中的 C2H callback 注入，随后出现 target-running 和 guest reset。

因此停止继续在 GDB callback 时序上堆补丁，按
`docs/core2-native-hci-backend.md` 转入 QEMU 内部 relay。本轮完成 HCI-1：
host H4 transport 和 bounded queue，不接 guest VHCI。

## 可复用设计

查阅公开 `0x504B0304/bes-qemu @ e57911d5` 的 Bluetooth bridge：

- `miband_hci_bridge.c` 提供 host H4/socket transport；
- `miband_hci_backend.c` 提供 backend 选择；
- `miband_bt.c` 使用 QEMU device queue，并在 main loop/vCPU 安全点提交；
- raw fd callback 不直接调用 guest callback。

本实现只提炼通用结构，不复制 BES SoC 寄存器、mailbox 或 vendor protocol。

## 实现

新增 QEMU 文件：

- `include/hw/xtensa/esp32_native_hci.h`
- `hw/xtensa/esp32_native_hci.c`

设备：

```text
TYPE_ESP32_NATIVE_HCI = "esp32-native-hci"
chardev=<QEMU chardev id>
```

功能：

- H4 command/event/ACL/SCO length parsing；
- 逐字节/分片输入累积，直到完整 packet；
- `32 × 2048` bounded RX/TX queues；
- queue full 时丢弃并记录 `last-error=2`；
- 未知 H4 type 计数为 malformed；
- peer open/close、RX/TX bytes/packets、queue depth、last error 通过
  QOM 可读属性暴露；
- reset 清空 framing 和 queue，保留 lifetime counters；
- unrealize 取消 chardev handlers；
- `esp32_native_hci_send_h2c()` 为后续 guest H2C 接入提供唯一写入入口。

## 验证

build：

```text
ninja -C .work/M5StopWatch-QEMU/build/qemu/build qemu-system-xtensa
PASS
```

patch：

```text
git apply --check  forward PASS
git apply --reverse --check  PASS
```

targeted transport：

```text
peer_opened                         true
event + fragmented ACL packets      true
rx_bytes=15                         true
initial queue depth=2               true
fill to 32                          PASS
33rd packet dropped                 PASS
last-error=queue_full               PASS
peer_closed                         PASS
qemu exit code 0                    PASS
```

平台：

```text
243/243 tests PASS
runtime coverage                   PASS
peripheral catalog                 PASS
QEMU profiles                      PASS
```

## 验证边界

- 这是 host transport-only；
- guest 尚未调用 `esp32_native_hci_send_h2c()`；
- C2H 尚未进入 QEMU device queue并送达 firmware callback；
- QEMU transport PASS 不等于 guest BLE、controller 或 RF PASS；
- 物理硬件 `NOT RUN`。

## 风险与回滚

- 后续 HCI-2/3 必须使用同一 transport，不得恢复 Python/GDB callback；
- queue overflow 必须中止对应 lease，不能丢弃后继续伪装 PASS；
- 回滚 QEMU patch 不影响现有 GDB diagnostic runner；
- repeated lease 在 HCI-4 前继续保持 `FAIL`，不能因 transport PASS 升级。

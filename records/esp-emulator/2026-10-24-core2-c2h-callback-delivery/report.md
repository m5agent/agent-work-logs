# Core2 QEMU 原生 HCI C2H callback 交付报告

## 背景

此前 QEMU `esp32-native-hci` 已完成：

- H4 chardev transport；
- bounded RX/TX queue 和 QOM counters；
- 从真实 `vhci_env_p` 捕获 stock H2C Reset。

但 guest 发完 Reset 后收不到 controller response，因此无法继续 HCI sequence。
之前直接调用 controller 内部 `vhci_send` 的假设已经失败：函数能返回，但
guest 仍等待 ACK 并超时。

## 根因与修复

匹配 ELF 和 GDB diagnostic bridge 表明正确入口是注册表
`vhci_env_p + 0x4e4` 的第二个函数：

```c
int (*notify_host_recv)(uint8_t *data, uint16_t len);
void (*notify_host_send_available)(void);
```

QEMU 实现：

1. 从匹配 ELF 解析 `vhci_env_p` 和 guest `malloc`；
2. 首次交付前调用 guest `malloc` 分配 C2H buffer，避免覆盖 BT RAM；
3. 用真实 VHCI length write 捕获完整 H2C packet；
4. 在 halted vCPU 安全点进入 guest callback；
5. 按 Xtensa call8 ABI：
   - caller `a10` 是 callee `a2` packet pointer；
   - caller `a11` 是 callee `a3` length；
   - caller `a8` 是 callee `a0` return address；
6. 保存/恢复 physical registers、PC、PS、window base/start、icount 和
   halted/interrupt 状态；
7. callback 成功后再调用 send-available；
8. 用 QOM 暴露 delivered/errors/status/steps/observed/return/exit PC。

## 验证

固件：

```text
sha256 906ba16439f8f8b421adb9ba3817ebf91d677498b0096c38e851a63570a8b680
size   16777216
```

QEMU：

```text
sha256 f5ec86620e29fa2854ecb0bff6c480a794757cb1e9fe62069352183434dfb15e
```

连续 5 次相同结果：

```text
guest H2C      01030c00  HCI Reset
controller C2H 040e0401030c00  Reset Complete
callback       status=0 errors=0
next guest H2C 01011000  Read Local Version
```

Tested commands：

```bash
ninja -C .work/M5StopWatch-QEMU/build/qemu/build qemu-system-xtensa
python3 tests/uiflow2/core2_native_hci/test_transport.py
python3 tests/uiflow2/core2_native_hci/test_guest_h2c.py \
  --image <stock-core2-image> --enable-c2h
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
```

结果：

```text
HCI-1 transport                     PASS
HCI-2 first H2C capture             PARTIAL/PASS
HCI-3a single-packet C2H callback   PASS 5/5
HCI-3b full HCI/GATT sequence       OPEN
HCI-4 repeated Device Service lease OPEN
platform tests                     243 OK
CI                                 243 tests, OK (skipped=2)
QEMU patch replay/build            PASS
```

## 验证边界

探索性 Bumble 运行曾完成完整 HCI 初始化、广播和 connection，但 GATT
service discovery 会间歇 timeout；也有运行停在第二条 HCI command。该状态
不稳定，未写成 PASS，也没有通过 retry 选择成功结果。

完整 Bumble HCI/GATT、NUS subscribe/write/notify、coexistence、RF、
physical cache/PSRAM 和真机仍需验证。QEMU callback boundary 不是
bit-exact Espressif BT controller/baseband。

## 风险与回滚

当前实现仍是实验性 controller-boundary relay。回滚源码提交
`5217b50af60c7ac31f3051a6fef8b70fdb110fe4` 可恢复 HCI-1/2 状态，不会改变
物理设备或已归档 evidence。

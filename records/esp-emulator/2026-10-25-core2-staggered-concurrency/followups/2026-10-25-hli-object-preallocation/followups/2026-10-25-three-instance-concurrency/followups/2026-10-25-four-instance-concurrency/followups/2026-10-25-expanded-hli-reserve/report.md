# ESP Emulator Core2 four-instance expanded HLI reserve 报告

## 背景

父记录已经证明四实例零错峰冷启动可达真实 concurrency `4`，但首批结果为
`1 PASS / 3 FAIL`：

- attempt 2 完成可见 WiFi、公网、GATT、PSRAM、frame/QOM 和 pcap，却以
  `hli-errors=1`、`hli-prealloc-failures=2` 被 aggregate health gate 拒绝；
- attempt 3/4 在 READY 前反复 panic：

```text
LoadProhibited @ 0x402630cc
ble_hs_hci_process_ack()
components/bt/host/nimble/nimble/nimble/host/src/ble_hs_hci.c:495
```

原始失败 evidence 和父记录结论保持不变。

## 根因

Bumble peer H4 日志表明 Reset、Read Local Version 等命令的 Command Complete
已由 controller 正常返回，问题位于 QEMU 向 guest HLI 注入 ACK 的路径。

`0008` 在 CPU0 idle 时预分配了 2 个真实 guest event buffer 和 2 个 ACL
mbuf。四条 guest 同时冷启动时，启动命令 burst 会耗尽该 reserve；CPU0
在等待 ACK 时没有再次到达 idle safe point，后续 Command Complete 只能等待
HLI backpressure，超过 NimBLE 的 2 秒 command-ack budget。于是 guest
读取缺失 ACK object 并 panic。

因此修复必须扩大真实 guest transport 对象池，不能用 host fixture 伪造
Command Complete、跳层写 guest 状态或绕过 HLI。

## 修复

`0009` 只修改 native-HCI reserve 常量：

```diff
-#define ESP32_NATIVE_HCI_HLI_EVENT_PREALLOC 2
-#define ESP32_NATIVE_HCI_HLI_ACL_PREALLOC 2
+#define ESP32_NATIVE_HCI_HLI_EVENT_PREALLOC 8
+#define ESP32_NATIVE_HCI_HLI_ACL_PREALLOC 4
```

对象仍由 guest allocator 分配，CPU0 繁忙时 QEMU 只填充已存在的真实
`os_mbuf`/event 对象并投递真实 HLI callback。

## 执行

两批独立运行使用相同 firmware、ELF 和 QEMU：

```text
attempts=4
concurrency=4
stagger-seconds=0
hold-seconds=120
timeout=300
require-psram
```

聚合结果：

```text
batch A: 4 requested, 4 completed, 4 passed, 0 failed
batch B: 4 requested, 4 completed, 4 passed, 0 failed
combined: 8/8 PASS
```

两批均绑定 launch assets，`input_assets_unchanged_during_run=true`。每个
lease 的结束 QOM depth 为 `8/4`，HLI `45/45`，C2H delivery 为
36 events/9 ACLs，错误、reset 和 panic 均为 0。

首批 attempt 2 在启动期记录 2 次 refill failure，随后对象池补满，全部
packet 仍走 fast path 并完成 45/45 HLI 投递；独立确认批没有 refill
failure。该恢复诊断被保留，不能从 evidence 中删除。

## 附带回归

`0009` 当前源码构建的 QEMU 还通过 Core2 六例外设组：

```text
6/6 cases PASS
24/24 checks PASS
attempts per case = 1
retry_used = false
```

该组覆盖触摸、RTC、电源键、扬声器/I2S DMA、麦克风/I2S RX、INA3221、
MPU6886 和 AXP192。它证明扩大 HLI reserve 没有破坏既有板级路径。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| source/build | `PASS` | `0009` patch reverse-check、源码 QEMU 构建和 CI |
| virtual cold start | `PASS` | 两批独立 `4×120s`，合计 `8/8` |
| guest HCI/HLI | `PASS` | 每 lease `45/45`，36 events/9 ACLs，depth `8/4` |
| WiFi/public network | `PASS` | DHCP、controlled HTTP、public DNS/HTTP |
| BLE GATT | `PASS` | external NUS scan/connect/write/notify |
| board/peripheral regression | `PASS` | Core2 六例 `6/6`、`24/24` checks |
| physical controller/PSRAM/RF | `NOT RUN` | 无物理设备或测量 |

## 验证边界

- 结论只覆盖当前绑定 firmware/ELF/QEMU/hook ABI 和最多四实例 workload；
- 四实例使用 QEMU functional controller/HCI 路径，不是 bit-exact
  Espressif controller/baseband；
- QOM PSRAM、网络和 frame 都是 virtual-device evidence；
- `8/8` 不能继承给五实例及更高并发、持续吞吐或其他 teardown；
- 父记录中的原始 `1/4` FAIL 必须保留。

## 风险与回滚

`0009` 增加的是 guest HLI transport reserve，不模拟 ACK，也不改变 host
firmware。回滚方式是 revert `35f5415` 或反向应用本记录 patch；回滚后四实例
启动 burst 会重新暴露 ACK object/queue 耗尽风险，不应作为稳定分支继续扩展
并发。

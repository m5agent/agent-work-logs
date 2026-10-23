# Core2 native HCI 完整 sequence 诊断报告

## 背景

- 来源：`CORE2-01`，阶段 `HCI-3b`。
- 已知：`HCI-1` transport、`HCI-2` 首包 H2C、`HCI-3a` 单包 C2H callback
  已通过。
- 目标：不使用 GDB，通过 QEMU native HCI 和 Bumble 完成
  scan/connect/service discovery，再进入 NUS subscribe/write/notify。

## 实现

新增 `tests/uiflow2/core2_native_hci/run_full.py`：

1. 从匹配 ELF 解析 `vhci_env_p`、`malloc` 和 idle symbol；
2. 启动 Bumble TCP controller/peer；
3. 启动一个 `m5core2` QEMU guest，使用 `esp32-native-hci` chardev；
4. 不启用 GDB；
5. 要求外部 peer scan、connect、NUS discovery、subscribe、write、notify；
6. 同时要求 guest `CORE2_HCI_BLE_RX` 和 `CORE2_HCI_BLE_ACK_SENT`；
7. 收集 serial、Bumble H4 trace、QOM counters 和退出状态。

QEMU 启动参数保持：

```text
tcg,thread=single
icount shift=auto,align=off,sleep=off
-m 0
-M m5core2
```

## 基线结果

恢复并重建已提交 native-HCI patch 后，真实运行结果：

```text
BLE advertisement found       PASS
BLE connected                 PASS
first ATT request reached     PASS
first ATT response sent       PASS
second ATT request received   PASS
GATT service discovery        FAIL
guest write/ACK               NOT RUN
notification ACK              NOT RUN
```

运行计数：

```text
h2c-packets       53
h2c-bytes        377
c2h-delivered     55
c2h-errors         0
c2h-last-status    0
send-available     4
rx-queue-depth     0
tx-queue-depth     0
malformed-packets 73
dropped-packets    2
```

## 失败时间线

```text
Bumble -> guest  ATT Read By Group Type Request
guest  -> Bumble  ATT response ACL
Bumble -> guest  HCI command complete / credit / second ATT request
guest              NimBLE: HCI process ack returned 12
guest -> Bumble  HCI Reset 01030c00
Bumble             GATT timeout
```

同一组事件字节在 GDB reference run 中可以继续到 NUS subscribe/write/notify
`5/5`。因此失败不是 Bumble 协议栈不会处理该固件，也不是固件单包格式错误。

## 诊断中排除的假设

### H4 RX 错位

临时私有 instrumentation 把 malformed 原因拆开后确认：

- RX type 错误：0；
- RX oversize：0；
- RX overflow：0；
- 73 次全部是 H2C length 字段的非最终写入。

有效完整长度写入仍正确发送到 Bumble，因此 H4 parser 不是当前失败点。

### Callback 拒绝

QOM 中 callback status 全部为 0，`c2h-errors=0`。问题不是 firmware
`notify_host_recv` 对单包返回错误。

### 固定 CPU0 idle

只允许 CPU0 halted/idle 时交付，会让 CPU0 忙时 C2H 队列积压，无法推进。

### 任意 CPU0 safe point

允许在任意 CPU0 safe point 交付，BLE 初始化出现 `ETIMEDOUT`，比 idle 路径
更差。

### 取消 RX 丢弃

增加队列背压后，完整 sequence 仍没有通过，且破坏 transport-only 已定义的
bounded-drop 契约。

以上实验均已从 QEMU worktree 恢复；native-HCI source 与仓库 patch
`git apply --reverse --check` 通过。没有把实验代码混入源码提交。

## 当前判断

失败余量集中在：

- H2C send 与对应 C2H response 没有形成显式 transaction；
- callback 直接由 QEMU safe point 注入，尚未建模 controller-to-host
  notification/IRQ 的真实上下文；
- guest host task 在等待 ACK 时可能 busy/transition，QEMU callback 注入后
  vCPU resume 与 FreeRTOS wake 顺序不可证。

下一项应实现 QEMU 内部的 response transaction 和 controller-to-host
notification 语义，再验证 ATT service discovery。继续调 sleep、CPU pinning
或 retry 不属于该阶段的正确修复。

## 验证

```text
test_transport.py
PASS (11/11 checks)

test_guest_h2c.py --enable-c2h
PASS (single-packet C2H callback)

run_full.py
FAIL (HCI-3b)

platform tests
Ran 253 tests
OK

GitHub Actions 40025648490
platform-contracts success
network-namespace-policy success
```

## 验证边界

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| transport | `PASS` | H4 framing、queue、drop、peer lifecycle |
| single C2H | `PASS` | Reset Complete callback 和 next H2C |
| BLE connect | `PASS` | 外部 Bumble peer |
| first ATT | `PASS` | request/response 双向 trace |
| service discovery | `FAIL` | second ATT 后 guest ACK 12 + Reset |
| bit-exact controller | `NOT RUN` | 仍是 HCI/controller-boundary 功能模型 |
| physical | `NOT RUN` | 无真机 |

## 风险与回滚

- 本次没有保留 QEMU scheduler 实验，也没有改变已发布 QEMU patch；
- runner 只用于诊断，不会在 CI 中被误当成 release PASS；
- 回滚源码提交 `32862edf3998cae4d4b62464c51af295761c330d` 可移除
  diagnostic gate 和文档更新；
- 无物理烧录或设备状态变更。

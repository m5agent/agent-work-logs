# ESP Emulator Core2 four-instance concurrency 报告

## 背景

前一阶段已经关闭 Core2 两实例和三实例 no-stagger `core2-native-hci`
门禁，但 Backlog 明确要求继续验证大于三实例的并发。此次工作同时承担代码、
文档和待办的重新整理，要求后续读者不能继续把四实例写成 `NOT RUN`，也不能
把三实例 PASS 自动继承给四实例。

执行参数：

```text
run_service_5x.py \
  --attempts 4 \
  --concurrency 4 \
  --stagger-seconds 0 \
  --hold-seconds 120 \
  --timeout 300 \
  --require-psram
```

所有输入在首个 lease 前绑定，运行期间 firmware、ELF、QEMU、runner、
Device Service、BLE 限制、网络策略和 HTTP fixture 哈希均未漂移。

## 执行结果

| attempt | 结果 | 关键事实 |
| --- | --- | --- |
| 1 | `PASS` | HLI `45/45`、errors/reset/panic 0、网络/GATT/PSRAM/evidence 完整 |
| 2 | `FAIL` | 可见工作完成，但 `hli-errors=1`、`hli-prealloc-failures=2` |
| 3 | `FAIL` | READY 前 `LoadProhibited @ 0x402630cc`，panic count 87 |
| 4 | `FAIL` | READY 前同地址 panic，panic count 85 |

聚合结果：

```text
attempts_requested=4
attempts_completed=4
attempts_passed=1
attempts_failed=3
concurrency_requested=4
maximum_concurrent_sessions=4
concurrency_observed=true
stagger_seconds=0
hold_seconds_per_attempt=120
```

因此四实例并发不是“脚本没跑到”或“基础设施未启动”，而是同一实现下的真实
virtual-device FAIL。

## 首个失败与符号化

attempt 2 的可见网络和 GATT 检查通过，但 QOM health counters 未归零：

```text
hli-errors=1
hli-prealloc-failures=2
```

runner 据此返回 aggregate FAIL。不能因为 frame/网络成功而忽略 controller
对象路径错误。

attempt 3/4 的首个 panic：

```text
Guru Meditation Error: Core 1 panic'ed (LoadProhibited)
PC: 0x402630cc
EXCVADDR: 0x00000000
```

用匹配 ELF 符号化：

```text
ble_hs_hci_process_ack
  at components/bt/host/nimble/nimble/nimble/host/src/ble_hs_hci.c:495
  (inlined by ble_hs_hci_cmd_tx at ble_hs_hci.c:604)
```

串口在首个 panic 前已有：

```text
NimBLE: HCI wait for ack returned 19
NimBLE: HCI process ack returned 12
```

说明失败落在 NimBLE command ACK 生命周期，而不是 WiFi、DNS、HTTP 或 BLE
GATT peer 的基础数据面。reboot 后反复出现的 `PC=0` 是首轮崩溃后的次生状态，
不能反向作为根因。

当前根因尚未完全关闭：现有证据可定位到 ACK object/queue 生命周期与四实例
启动负载，但还缺少对 `l_ble_hs_hci_ack` 为空与其 HCI command 序列的
逐包关联。下一步应先修四实例 ACK/预分配竞态，再做两批独立复跑。

## 代码与文档整理

本次源码变更没有修改 QEMU controller 行为，只完成：

1. 将四实例失败 evidence 纳入源码仓库和文档契约；
2. 更新 README、project status、Backlog、workstreams、code map、
   Device Service API、user firmware matrix、validation ledger 和
   Core2 backend 专题；
3. 把“大于三实例 NOT RUN”统一改为“四实例已执行并 FAIL，scale-out 开放”；
4. 修正过于宽泛的 `0007/0008 FAIL → FIXED` 叙述，限定为当时双实例边界；
5. 新增 `DOC-01`：跟踪近 6000 行文档契约测试按领域拆分和
  结构化 stale-claim 清单；
6. 说明 `run_service_5x.py` 文件名是为 evidence 路径/哈希兼容保留，
   实际已经参数化为任意 attempts/concurrency。

## 验证

```text
platform unittest       465/465 PASS
docs consistency         36/36 PASS
QEMU profiles            19/19 PASS
Node SHA256/upload        2/2 PASS
runtime coverage         PASS
peripheral catalog       PASS
QEMU profiles check      PASS
project snapshot check   PASS
worker fleet migration    PASS
Ruff E9/F                PASS
compileall               PASS
git diff --check         PASS
GitHub Actions           PASS
```

CI：
<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40178287662>

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build/static | `PASS` | 465 项平台测试、文档/API/profile/snapshot 与 CI |
| virtual network | `PASS`（attempt 1/2 可见路径） | DHCP、public DNS/HTTP、pcap |
| BLE GATT | `PARTIAL` | attempt 1 PASS；attempt 2 health FAIL；attempt 3/4 未 READY |
| concurrent cold start | `FAIL` | `1 PASS / 3 FAIL` at real concurrency 4 |
| controller health | `FAIL` | HLI error/prealloc failure 与 NimBLE ACK panic |
| documentation reconciliation | `PASS` | 当前事实、证据、Backlog 和 stale-claim 契约同源 |
| physical hardware | `NOT RUN` | 无物理设备或测量 |

## 边界

- 四个 QEMU 共享同一个 macOS host 和 Device Service，不是物理多机；
- native-HCI 是功能级 QEMU relay，不是 bit-exact Espressif BT
  controller/baseband；
- `0x402630cc` 的符号化只证明首个 guest crash 位置，不单独证明 QEMU 或
  firmware 哪一行拥有最终根因；
- PSRAM、network、frame 和 QOM 都是虚拟设备证据；
- 三实例 `6/6`不能继承给四实例。

## 风险与回滚

- 本记录不引入 controller 行为改动；
- 文档/测试/evidence 变更可通过 revert `4b6c379` 回滚；
- 回滚后仓库会重新把四实例写成“更多实例 NOT RUN”，丢失实际失败证据，
  不应作为后续开发分支；
- 四实例修复实现仍待后续 follow-up，不能修改本条原始 FAIL。

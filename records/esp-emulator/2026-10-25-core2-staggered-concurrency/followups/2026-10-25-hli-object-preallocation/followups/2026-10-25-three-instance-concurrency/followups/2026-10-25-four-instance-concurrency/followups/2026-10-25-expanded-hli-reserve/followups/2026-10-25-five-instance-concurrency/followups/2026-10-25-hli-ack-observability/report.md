# ESP Emulator Core2 HLI ACK observability 报告

## 背景

五实例 30 秒错峰稳态已由父记录的两批 `10/10 PASS` 覆盖，但相同实现的
零错峰冷启动仍不稳定。先前 evidence 已把 panic 符号化到
`ble_hs_hci_process_ack()` 的 null ACK opcode 读取
`0x402630cc`，但还缺少以下区分：

- 初始 semaphore/ACK state 是否已经被污染；
- response 是否及时从 Bumble 进入 guest HLI；
- 旧 response 是否在 guest 推进到下一命令后才被投递；
- cache/PSRAM 或 HCI transaction 本身是否为首因。

## 实现

`0010` 只增加 opt-in trace：

- `trace-hci-rx-evt-pc`：进入 `ble_hs_hci_rx_evt`；
- `trace-hci-rx-ack-check-pc`：semaphore-count 分支；
- `ble-hs-hci-ctx-address`：读取真实
  `ble_hs_hci_ctx->hci_ack`；
- trace 输出增加 `a6/a10`，用于记录该分支的 semaphore count。

这些参数只由 `M5_CORE2_HCI_PACKET_TRACE=1` 注入。无该环境变量时，
Device Service 构造的 QEMU 参数不包含新 trace PC，默认行为与 `0009`
一致。

## 执行

服务配置：

```text
core2-native-hci
qemu-unified
gdb_bridge=false
attempts=5
concurrency=5
stagger-seconds=0
hold-seconds=20
require-psram
M5_CORE2_HCI_PACKET_TRACE=1
```

聚合结果为 `3 PASS / 2 FAIL`，maximum concurrency `5`，输入资产无漂移。

默认路径对照使用同一 firmware/ELF/QEMU，关闭 packet trace：

```text
attempts=1
concurrency=1
hold-seconds=10
require-psram
```

结果为 `1/1 PASS`。

## 失败时间线

失败 attempt 1 的 host trace：

1. `hci_cmd_tx` 发出 `0x0c03` HCI Reset；
2. Bumble 返回 `040e0401030c00`；
3. QEMU 没有及时进入 HLI；
4. guest 累计发出三次 Reset，前两次已在 ACK timeout 后调度 reset；
5. 第一条 HLI 在 Bumble response 后 `4.506306s` 才投递；该值是 host trace
   time，不是 guest 虚拟时钟；
6. 该 event 进入 ACK 检查时 `hci_ack=NULL`、semaphore count `0`；
7. guest 开始新的 `0x1001` command；
8. 多个迟到的 Reset Complete 与新 command/response 交错；
9. `ble_hs_hci_process_ack` 发现 opcode mismatch，error `12`；
10. guest 进入 reset loop，之后在 `0x402630cc` `LoadProhibited`；
11. reboot 后的 `PC=0` 是次生故障。

这证明首因不是 stale ACK pointer/semaphore state，而是 response 在 HLI
外的驻留时间和
旧 response 的迟到投递。

## 被否决实验

| 实验 | 结果 | 处置 |
| --- | --- | --- |
| receive 后立即调度 HLI | 缩短部分窗口，但零错峰仍失败 | 未合入 |
| pending consumption 自观察 | 批次仍低于全通过 | 未合入 |
| HLI ready 前阻塞 H2C | startup/GATT failure 仍存在 | 未合入 |
| 多飞行 HLI post | 无 trace 五实例 `0/5` | 拒绝 |

没有通过扩大 NimBLE timeout、自动 retry、伪造 ACK 或持续 IRQ kick 来
制造 PASS。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU 重新编译；`0010` reverse-check PASS；CI 两个 job PASS |
| opt-in trace | `PASS` | ACK pointer、semaphore 分支和迟到 packet 顺序可读 |
| default path | `PASS` | trace-off 单 lease `1/1`，HLI `45/45`，errors/panic 0 |
| documentation reconciliation | `PASS` | catalog/profile、状态/Backlog/交接页和回归测试统一把 `4.506306s` 标为 host trace time，不是 guest 虚拟时钟 |
| zero-stagger five instances | `FAIL` | `3/5 PASS`；保留 aggregate、trace、serial、peer |
| behavioral fix | `NOT RUN` | 四个候选均不稳定或回退，未合入 |
| physical controller/PSRAM/RF | `NOT RUN` | 无物理测量 |

仓库验证：

```text
platform tests: 479/479 PASS
docs contracts: 37/37 PASS
node units: 2/2 PASS
runtime coverage / peripheral catalog / QEMU profiles / snapshot: PASS
compileall / Ruff E9,F / git diff --check: PASS
CI: PASS
```

## 验证边界

- `0010` 是诊断能力，不是五实例修复；
- PASS 的单实例只证明默认路径未回归；
- 失败为 virtual-device functional workload，不代表固件在真机失败；
- 物理 cache/PSRAM timing、RF 和 bit-exact controller 均未验证。

## 风险与回滚

观测在 trace 关闭时无设备参数变化，风险仅限开启 trace 时的日志量和
调度扰动。回滚方式是 revert `473e613` 或反向应用 `0010` patch。

下一项修复应针对 HLI readiness 与 response ordering，并重新跑独立的
五实例零错峰批次；在通过前不得把 `CORE2-02` 标为完成。

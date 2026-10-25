# ESP Emulator Core2 HLI object preallocation 报告

## 背景

上一 follow-up 关闭了两个局部问题：

1. extended BLE exchange 的 GATT request/notification timeout 从
   `10/15s` 扩到 `30s`；
2. QEMU `0007` 只在观察到有效 guest scheduler/meta queue 后才安排 HLI。

`0007` 后首批四 lease 为 `4/4 PASS` 且 `hli-errors=0`，但独立复核仍在
无错峰同时冷启动时出现一个 guest
`LoadProhibited at ble_hs_hci_process_ack`。该失败没有被重试或后续 PASS
覆盖。

## 根因

packet trace 将问题拆成 controller response 与 host HLI delivery 两段：

```text
Bumble controller response: about 4.6ms
receive -> HLI callback:    about 3.660s
NimBLE HCI command timeout: 2s
```

旧 HLI 路径在 CPU0 执行 cache-sensitive controller code 时，需要使用 guest
allocator 和 `os_mbuf` API 完成 nested guest call。ACL FIFO head 需要等待
该调用，后面的 Command Status/LE Meta 也被阻塞。超过 guest HCI timeout 后，
NimBLE 进入 reset/错误 ACK 路径，最终在 ACK 处理处 panic。

这不是 `0007` valid-queue 问题，也不是 Bumble 单纯返回过晚：controller
response 已经及时到达，阻塞发生在 QEMU 向 guest HLI 交付真实对象的阶段。

## 实现

QEMU patch
`0008-esp32-native-hci-preallocate-hli-objects.patch`：

- CPU0 idle 时调用真实 `ble_transport_alloc_evt(0)`，保留两个 event
  buffer；
- CPU0 idle 时调用真实 `ble_transport_alloc_acl_from_ll()`，保留两个 ACL
  mbuf；
- CPU0 busy 时直接按匹配 ESP-IDF v5.5.4 的 32-bit `os_mbuf` 布局填充
  `om_data`、`om_len` 和 packet header length；
- 继续投递真实 `ble_transport_to_hs_evt_impl` /
  `ble_transport_to_hs_acl_impl` callback 和真实 HLI queue/IRQ；
- 无 spare object 时保留原 halted/idle guest-call fallback；
- 新增 `hli-fast-path-events`、`hli-fast-path-acls`、
  `hli-event-prealloc-depth`、`hli-acl-prealloc-depth` 和
  `hli-prealloc-failures` QOM 计数器。

runner 新增 fast-path/preallocation counter 解析，并要求至少一个真实
guest-object fast-path packet；session evidence 另外逐 lease 检查最终
36 events/9 ACLs、spare depth 和 failures。

## 执行结果

### 无错峰双实例并发

| 批次 | 请求 | PASS | FAIL | 最大并发 | 错峰 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 4 | 4 | 0 | 2 | 0s |
| B | 4 | 4 | 0 | 2 | 0s |

每批是两个双实例冷启动对。两批独立 evidence 的 QEMU/tool hashes一致；
每个 lease：

- event fast path `36/36`；
- ACL fast path `9/9`；
- HLI `45/45`；
- event/ACL spare depth `2/2`；
- `hli-errors=0`；
- `hli-prealloc-failures=0`；
- scheduler reset 和 panic 为 0。

latency 对照中，旧路径约 `3.660s`，超过 `2s` timeout；`0008` 约
`0.328s`，低于 timeout。

### 完整回归

`0008` 版本重新运行完整 UIFlow2 外设矩阵：

- `67/67` case PASS；
- `274/274` check PASS；
- 全部 `attempts=1`、`retry_used=false`；
- Core2 六个 case `24/24` check PASS；
- QEMU `f2bc2b4d…`；
- runner `770db317…`；
- 原始 summary SHA-256 `f5029d96…`。

平台、文档、profile、snapshot、Node、Ruff、compileall、JSON parse、
`git diff --check` 和 QEMU patch reverse-check 均通过。GitHub Actions
`40174318654` 的 `platform-contracts` 与 `network-namespace-policy`
两个 job 也均 `PASS`。

## 代码与文档对账

本轮把后期事实同步到稳定入口：

- `project-status.md`：双实例 `8/8`、`0008` latency、完整 matrix 新日期，
  并把 `CORE2-02` 剩余工作明确为 `P0`；
- `project-backlog.md`：优先级和“网络 → Core2 → 固件安全/Manifest”执行
  顺序统一；
- `device-service-api.md`：修正“Core2 三十轮”和 `features.network`
  受环境门控的语义，加入 no-stagger `8/8`；
- `core2-native-hci-backend.md`、network/Core2 专题和 tests README：
  保留历史失败，标明由 `0008` 取代；
- 设备 catalog/profile/generated README、`project-snapshot.md` 和
  `validation-ledger.md` 同步生成；
- 文档契约测试新增 `0008`、`8/8`、P0、完整 matrix evidence 和历史旧结论
  回流门禁。

## 验证边界

所有结果是 virtual-device validation：

- 不证明物理 PSRAM/cache timing；
- 不证明 Espressif BT baseband/controller bit-exact；
- 不证明 RF、天线、功耗、声学或电气；
- 不证明 physical hardware；
- 当前 QEMU hook offsets 只对绑定 UIFlow2 v2.5.3 build 成立；
- `8/8` 只覆盖两个实例、指定固件、ELF、QEMU 和 hook ABI。

## 回滚

`0008` 可单独 reverse apply，回到 `0007` 的 idle/halted guest-call 路径。
回滚后必须把两实例无错峰 cold start 恢复为 `OPEN`，并保留本记录的
`8/8` evidence 作为历史；不能继续把 `0007` 单批 PASS 写成 cold-start
closed。

源码回滚对应 `bf98ea8d…` 的 reverse commit；设备 catalog、profile、自动
快照和当前状态文档应随源码一起回滚，避免重新出现“代码修复、文档仍 OPEN”
或相反的状态漂移。

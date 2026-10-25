# Core2 fixed-icount six-instance cold start 报告

## 背景

五实例零错峰门禁在固定 icount 和 BLE-first workload 下已经 `10/10 PASS`，
但 `CORE2-02` 仍要求验证更大并发。此次在相同输入和相同 Device Service
路径上把每个 batch 扩展到六个同时冷启动的 QEMU，并保持 120 秒 hold。

目标不是放宽断言，而是验证同一 guest 内 WiFi、公网、外部 BLE GATT、
PSRAM stress、frame、QOM、pcap 和 evidence 是否能在真实并发 6 时全部成立。

## 执行

- 使用已冻结 firmware `c3eaa35b…`、ELF `5bec056b…`、QEMU
  `d238e2f8…` 和同一 runner/service/tool hashes。
- 通过真实 `/api/v1` 创建六个独立 lease，`stagger_seconds=0`，
  `hold_seconds=120`，`maximum_concurrent_sessions=6`。
- 每个 QEMU 均从实际进程命令行确认
  `tcg,thread=single,tb-size=128` 和
  `shift=5,align=off,sleep=off`。
- 两批独立执行，每批 `6/6 PASS`，合计 `12/12`。

## 证据

| 批次 | 结果 | PSRAM sweeps | evidence SHA-256 |
| --- | --- | --- | --- |
| A | `6/6 PASS` | `13,12,13,13,13,12` | `ae49660be9ad1b67e8149bad46069e8c86e7c5892ca7148bac8828aca642751a` |
| B | `6/6 PASS` | `13,13,13,13,13,13` | `6131b3c61a99bba93f45b50e34d0f114ea7142405cce4ef1352377ebf71d9b58` |

两批共完成 154 次 1 MiB 全缓冲读回。每个 lease 的 frame SHA-256 均为
`cd2f2033fa92dabd8a60dd4e81bbefd3656b855123e762aef5080188ddf5192f`，
QOM 为 31 节点 / `8,388,608 B`。

每个 lease 均为：

- WiFi DHCP/HTTP、公网 DNS/HTTP、external NUS GATT PASS；
- HLI `45/45`、36 events、9 ACLs；
- reset、panic、dropped、TX/meta/HLI queue depth 为 0；
- active BLE link 在 hold 结束时仍成立；
- pcap 与 evidence ZIP 均存在。

第二批 attempt 6 记录 `hli-prealloc-failures=1`，但之后仍完成全部
36/9 fast-path packet 和 45/45 HLI 投递。该瞬时 refill 计数没有造成
HCI error、ACK mismatch、reset 或 panic，因此保留为可见诊断而不是隐藏。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `NOT RUN` | 复用已构建并冻结的 test image，未做 clean rebuild |
| flash | `PASS` | 12 个 lease 均经真实 Device Service firmware/session 路径启动 |
| transport | `PASS` | 外部 NUS GATT、HLI 45/45、每 session pcap |
| device_response | `PASS` | frame、31 节点 QOM、WiFi/public HTTP |
| data_behavior | `PASS` | 12 个 guest 共 154 次 1 MiB PSRAM 全缓冲读回 |
| visual_or_physical | `NOT RUN` | 无物理屏幕、RF、功耗或电气测量 |

项目验证：

- platform tests `491/491 PASS`
- docs contracts `37/37 PASS`
- browser unit tests `2/2 PASS`
- runtime coverage、peripheral catalog、QEMU profile、project snapshot、
  compileall、Ruff `E9/F` 和 `git diff --check` PASS
- GitHub Actions run `40195028961` 的 `platform-contracts` 与
  `network-namespace-policy` 均 PASS

## 验证边界

结论只覆盖当前 firmware SHA、ELF、QEMU build、`core2-native-hci` hook ABI、
六个同时冷启动的 lease 和 120 秒窗口。固定 icount 是确定性虚拟时间，不代表
实时性能或物理 cache/PSRAM timing。

大于六实例、持续吞吐、active-stop 之外 teardown、bit-exact
controller/baseband、物理 RF 和真机仍需独立验证。

## 风险与回滚

本轮仅增加测试和 evidence，没有改变 Core2 运行时实现；回滚提交 `c72ac2f`
不会改变设备运行路径。已提交的历史失败和五实例 evidence 不应删除。

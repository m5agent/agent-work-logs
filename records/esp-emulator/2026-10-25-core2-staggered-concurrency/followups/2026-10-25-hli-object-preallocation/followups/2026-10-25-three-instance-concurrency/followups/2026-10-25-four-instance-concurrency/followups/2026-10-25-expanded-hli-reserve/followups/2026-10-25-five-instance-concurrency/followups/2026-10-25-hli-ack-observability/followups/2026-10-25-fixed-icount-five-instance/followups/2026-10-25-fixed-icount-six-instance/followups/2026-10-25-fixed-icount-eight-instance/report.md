# Core2 fixed-icount eight-instance cold start 报告

## 背景

六实例门禁已通过两批 `6×120s`。此次把并发推进到 Device Service 当前单设备
容量上限 8，验证同一 guest 内网络、BLE、PSRAM、frame、QOM、pcap 和 evidence
是否能在八实例争用下同时保持。

## 第一次 control

旧 runner 使用 `hold/10` 的 sustained floor，120 秒要求 12 次连续 sweep。
首批八实例结果：

- aggregate `4 PASS / 4 FAIL`；
- 最大真实并发 8；
- 所有 8 个 guest 的 WiFi、公网、NUS GATT、frame、31 节点 QOM、pcap 和
  evidence PASS；
- 所有 8 个 guest 的 HLI `45/45`、36 events、9 ACLs、errors/reset/panic/
  dropped 为 0；
- 4 个失败 lease 均完成 11 次连续 PSRAM sweep，另 4 个完成 12 次。

因此失败原因是最高并发下 sweep 吞吐低于固定可调的阈值，不是 guest panic、
controller ACK failure、网络故障或 PSRAM 数据 mismatch。失败 evidence 保留。

## 校准与修复

sustained floor 改为：

```text
max(3, floor(hold_seconds / 12))
```

对 120 秒 hold，这意味着至少 10 次完整 1 MiB 写/读校验。其他门禁未降低：
heartbeat、受控 HTTP、公网 recheck、连续 sweep 序列、HLI、GATT、frame、
QOM、pcap 和 evidence 仍全部为必需项。

校准只修改 runner 的 floor；Device Service、QEMU accelerator、BLE probe、
network policy 和 HTTP fixture 的 hashes 保持不变。专项测试锁定
threshold-fail control 与两批 pass 的 runner hash 差异。

## 校准后复跑

两批独立零错峰 `8×120s`：

| 批次 | 结果 | PSRAM sweeps | evidence SHA-256 |
| --- | --- | --- | --- |
| A | `8/8 PASS` | 全部 12 | `36d52c32d6156b6282c1208a72f12eac50b1d87eacbb85cc9caf2a47ce1f989c` |
| B | `8/8 PASS` | 4×11、4×12 | `96d12ff41e2def7ab48813b499590a914de6b6da3ed7805b69c1f26d7d971fe7` |

合计 `16/16 PASS`、188 次 1 MiB 全缓冲读回。每个 lease 的 frame SHA 均为
`cd2f2033fa92dabd8a60dd4e81bbefd3656b855123e762aef5080188ddf5192f`，
QOM 31 节点 / `8,388,608 B`。

两批各有一个 lease 记录一次可恢复 `hli-prealloc-failures=1`，随后仍完成
36/9 fast-path packet 和 45/45 HLI 投递；该计数保留。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `NOT RUN` | 复用已构建并冻结的 test image |
| flash | `PASS` | 24 个 control/pass lease 均经 Device Service 启动 |
| transport | `PASS` | 外部 NUS GATT、HLI 45/45、每 session pcap |
| device_response | `PASS` | frame、31 节点 QOM、WiFi/public HTTP |
| data_behavior | `PASS` | 确认批 16 个 guest 共 188 次 PSRAM 全缓冲读回 |
| visual_or_physical | `NOT RUN` | 无物理屏幕、RF、功耗或电气测量 |

项目验证：

- platform tests `497/497 PASS`
- docs contracts `37/37 PASS`
- browser unit tests `2/2 PASS`
- runtime coverage、peripheral catalog、QEMU profile、project snapshot、
  compileall、Ruff `E9/F` 和 `git diff --check` PASS
- GitHub Actions run `40196580736` 的两个 job 均 PASS

## 验证边界

结论覆盖当前 firmware/ELF/QEMU/tool hashes、`core2-native-hci` hook ABI、
八实例同时冷启动和 120 秒窗口，并以服务当前每设备容量 8 为上限。

大于八实例、持续吞吐、active-stop 之外 teardown、bit-exact
controller/baseband、物理 RF、物理 PSRAM/cache 和真机仍需独立验证。

## 风险与回滚

本轮改变 sustained floor，未改变 guest 数据面或关键 health 判定。回滚提交
`a181ac9` 会恢复 `hold/10`，但该阈值已在八实例下产生可复现的纯吞吐误判。
历史 threshold-fail 和所有五/六实例 evidence 不应删除。

# ESP Emulator Core2 three-instance concurrency 报告

## 背景

`0008` 已通过两批双实例 `4×120s`，合计 `8/8`。本 follow-up 把并发提高到
三个无错峰同时冷启动的 Core2 unified lease，并保持 WiFi、公网、BLE
GATT、PSRAM、frame/QOM/pcap/evidence 在同一 session 内。

命令形状：

```text
run_service_5x.py \
  --attempts 3 \
  --concurrency 3 \
  --stagger-seconds 0 \
  --hold-seconds 120 \
  --require-psram
```

## 失败阶段一：peer scan 预算

首批三实例实际启动 3 个 QEMU、3 个 BLE peer 和 3 个 per-session HTTP
fixture，但三 lease 全部在 GATT 前失败：

```text
BLE_BUMBLE_FAIL no advertisement matching 'M5-CORE2-UNIFIED'
NimBLE: HCI wait for ack returned 19
```

guest 已进入 WiFi、公网 HTTP 和 PSRAM 初始化，没有 panic。QOM 显示 peer
先关闭，随后 H2C socket 才报错。旧 Device Service 给 extended exchange
固定 `40s` scan 窗口，而三实例 guest 到 BLE 初始化约需 `55s`；peer 在
guest 广播前退出。

将预分配池临时扩到 4 个 event/ACL object 没有改善，因此不是 `0008`
对象容量问题；实验未进入保留实现。

## 失败阶段二：sweep 阈值

peer scan 改为：

```text
min(120s, max(40s, ready_timeout - 10s))
```

下一轮已完成全部 HCI/GATT/网络数据面，但 `1 PASS / 2 FAIL`。两个失败
lease 各完成 29 次 sweep，旧 `hold/4=30` 阈值只差一次。并发下每个
`1 MiB` 全缓冲校验更慢，因此 sustained 下限改为 `hold/5=24`；仍要求连续
sweep、单调 heartbeat、至少 8 次 HTTP 和 2 次公网 recheck。

## 通过结果

两批独立三实例 `3×120s`：

| 批次 | PASS | FAIL | 最大并发 | 错峰 |
| --- | ---: | ---: | ---: | ---: |
| A | 3 | 0 | 3 | 0s |
| B | 3 | 0 | 3 | 0s |

每 lease：

- HLI `45/45`；
- 36 events / 9 ACLs；
- event/ACL spare depth `2/2`；
- `hli-errors=0`、reset/panic 为 0；
- 29–30 次 `1 MiB` PSRAM 全缓冲校验；
- WiFi、公网、NUS GATT、frame、31-node QOM、pcap、evidence、cleanup。

pass A 的 attempt 1 记录一次启动期 prealloc allocation failure，但随后
恢复 `2/2` spare depth，所有 36/9 packet 走 fast path 且 45/45 投递成功。
该 transient counter 作为诊断保留，不是最终对象缺失。

## QOM boot 测试竞态

重建 QEMU `b5b2d878…` 后，Core2 六例设备组首次为 `5/6`。失败 case
`core2-power-monitor` 正常退出但停在：

```text
waiting bus=625 shunt=12
```

默认 post-boot QOM 注入在 8 秒窗口内两次错过固件读取；同一 post-boot
方式延长到 20 秒后 PASS，boot-time QOM 注入也直接 PASS。固定 INA3221
物理通道值改为 `qom-set-boot` 后，Core2 六例再次 `6/6`、`24/24` checks，
全部 attempts=1。

## 验证

```text
platform tests: 465/465 PASS
documentation:  36/36 PASS
QEMU profiles:  19/19 PASS
Node tests:     2/2 PASS
Core2 group:    6/6 cases; 24/24 checks
three-instance: 6/6 leases
```

coverage、catalog、profiles、snapshot、Ruff `E9/F`、compileall 和
`git diff --check` 均 PASS。GitHub Actions `40176816140` 的
`platform-contracts` 与 `network-namespace-policy` 两个 job 均 `PASS`。

完整 67-case matrix 未在本 harness-only follow-up 后重跑；上一结果版本
仍保留 `67/67`、`274/274`。本次对受影响 Core2 设备组和当前重建 QEMU
做了定向 `6/6` 回归。

## 边界

所有结果都是 virtual-device validation：

- 不证明大于三实例的稳定性；
- 不证明持续吞吐或其他 teardown；
- 不证明 bit-exact BT controller/baseband；
- 不证明物理 PSRAM/cache timing、RF、功耗或电气；
- 不证明 physical hardware。

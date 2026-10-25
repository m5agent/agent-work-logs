# ESP Emulator Core2 sustained PSRAM 与周期联网压力报告

## 背景

上一轮已证明 Core2 guest 能从 QOM 生效的 4 MiB 虚拟堆分配 1 MiB 并完成三次
全缓冲读回，但三次校验不足以证明持续稳定性，也没有覆盖 hold 期间网络是否
持续可用。

本轮目标是在同一 `qemu-unified/core2-native-hci` guest 中同时保持：

1. PSRAM 1 MiB 数据模式长时间可读；
2. WiFi 与受控 HTTP；
3. 公网 DNS/HTTP；
4. active BLE NUS GATT；
5. bounded TCG、frame/QOM 和 pcap evidence。

## 实现

- guest 在 READY 后每 2 秒执行一次 1 MiB 全缓冲校验；
- 每 10 秒重做受控 HTTP，并记录 `HTTP_RECHECK_PASS`；
- 每 30 秒重做公网 DNS/HTTP，并记录 `PUBLIC_RECHECK_PASS`；
- 每 10 秒输出 elapsed、PSRAM sweep、HTTP recheck、public recheck 的
  `STRESS_HEARTBEAT`；
- runner 根据 hold 时长计算最低 sweep、heartbeat、HTTP/public recheck；
- heartbeat 计数必须单调，最终 marker 数不得少于 heartbeat 中已报告数；
- 任一 PSRAM、HTTP 或 public recheck error 直接失败。

## 阈值校准失败

首次正式 `3×120s` 运行中，第一个 lease 已完成 35 次 PSRAM 校验、10 次 HTTP、
3 次公网 recheck，active BLE 和 bounded TCG 全部正常，没有 panic。但 runner
把最低 sweep 设为 `hold/3=40`，高于当前 MicroPython/QEMU 实际速率，聚合结果
误判 FAIL。

失败 evidence 保留。阈值改为保守 `hold/4=30`，并新增 heartbeat/final counter
一致性检查后重新运行。该失败属于 harness 校准，不是 PSRAM、WiFi 或 BLE 故障。

## 执行结果

| Lease | PSRAM sweeps | 读取量 | HTTP | Public | pcap | HLI | QOM |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 36 | 36 MiB | 10 | 4 | 25,267 B / 222 packets | 45/45 | 34 |
| 2 | 35 | 35 MiB | 10 | 3 | 22,912 B / 205 packets | 45/45 | 34 |
| 3 | 35 | 35 MiB | 10 | 3 | 23,418 B / 211 packets | 45/45 | 34 |

三轮 frame SHA256 一致；HLI errors、HLI/meta/TX queue、dropped、last-error、
peer-close 和 panic 均为 0。每轮 4 个 host resource sample 的 RSS delta 为
`+656/+48/+112 KiB`，仅用于当前 120 秒 workload。

pcap summary 显示：

- 三次均有 DHCP DISCOVER/OFFER/REQUEST/ACK；
- DNS 查询包含 `example.com.`；
- flows 分别 53、46、48；
- pcap truncated/malformed records 为 0。

## 验证

```text
Core2 sustained PSRAM/network   3/3 PASS
platform contracts              418/418 PASS
documentation contracts         23/23 PASS
Node upload/SHA/UI              3/3 PASS
runtime coverage                PASS
peripheral catalog              PASS
QEMU profiles                   PASS
project snapshot                PASS
compileall                      PASS
Ruff fatal checks               PASS
git diff --check                PASS
GitHub Actions 40150023648      PASS
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、资产/工具哈希、profile/catalog checks |
| transport | `PASS` | native HCI/HLI、Device Service API |
| device_response | `PASS` | frame/QOM、周期 WiFi/公网、NUS GATT |
| data_behavior | `PASS` | 106 MiB 全缓冲校验、30 次 HTTP、10 次公网 |
| visual_or_physical | `NOT RUN` | 无物理 PSRAM/cache timing、RF 或真机 |

## 未覆盖与风险

- 120 秒不等于数小时 soak；现有两小时 soak 不包含本轮持续 PSRAM sweep；
- 不验证板载物理 8 MiB、cache miss 延迟、PSRAM 带宽或电气行为；
- 不证明 bit-exact BT controller/baseband；
- 不覆盖长时并发/吞吐、其他 teardown、物理 RF、功耗或真机。

## 回滚

回滚 `2a3e8120c5548110fad032d0172a3f7dd7a15e13` 即可恢复到上一版
`b4b793127dd3351ed4a7b398ab1e0de810d17ab0` 的三次读回门禁。回滚不涉及
物理设备、凭据或不可逆状态。

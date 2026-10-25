# ESP Emulator Core2 600-second PSRAM soak report

## 背景

`3×120s` 已证明 short multi-minute sustained PSRAM/network stress。为补强
Core2 cache/PSRAM 稳定性，本轮不修改实现，使用已提交的相同
firmware/runner/QEMU 将单 lease 扩展到 600 秒。

## 执行

```text
runtime=qemu-unified
profile=core2-native-hci
attempts=1
hold-seconds=600
ble-linger=660
ble-reconnect-cycles=1
require-psram=true
accelerator=tcg,thread=single,tb-size=128
```

guest 在 READY 后持续周期性执行：

- 1 MiB PSRAM pattern/address-tag 全缓冲校验；
- controlled HTTP；
- public DNS/HTTP；
- heartbeat 输出。

## 结果

| 项目 | 结果 |
| --- | --- |
| lease | `1/1 PASS` |
| hold | 600 秒 |
| PSRAM sweeps | 179 |
| verified bytes | 187,695,104 B |
| controlled HTTP | 51 |
| public recheck | 18 |
| active BLE | PASS |
| HLI | 45/45 |
| frame/QOM | 3,731 B / 34 nodes |
| pcap | 97,951 B / 912 packets / 208 flows |
| cleanup | PASS |
| panic/queue/dropped/peer-close | 0 |

20 个 host resource sample：

- RSS `327472→327824 KiB`，delta `+352 KiB`；
- phys footprint `246784→187392 KiB`，delta `-59392 KiB`。

该样本只描述本次虚拟运行，不是物理内存或 cache 时序测量。

## 验证

```text
Core2 PSRAM 600-second soak   1/1 PASS
platform contracts            418/418 PASS
documentation contracts       23/23 PASS
Node upload/SHA/UI            3/3 PASS
runtime coverage              PASS
peripheral catalog            PASS
QEMU profiles                 PASS
project snapshot              PASS
compileall                    PASS
Ruff fatal checks             PASS
git diff --check              PASS
GitHub Actions 40150913419    PASS
```

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | compileall、输入/工具哈希、profile/catalog |
| transport | `PASS` | native HCI/HLI、Device Service |
| device_response | `PASS` | frame/QOM、周期 WiFi/公网、NUS GATT |
| data_behavior | `PASS` | 179 次 PSRAM 全缓冲校验、51 HTTP、18 public |
| visual_or_physical | `NOT RUN` | 无物理 PSRAM/cache timing、RF 或真机 |

## 未覆盖与风险

- 不验证物理 8 MiB PSRAM、带宽、cache miss 或电气行为；
- 不证明 bit-exact BT controller/baseband；
- 不与 artifact-bound 7200 秒 soak 合并，因此两小时连续 PSRAM 校验仍
  `NOT RUN`；
- 不覆盖长时并发、其他 teardown、RF、功耗或真机。

## 回滚

该运行只新增 evidence 与文档；回滚 `a9d60e1` 即可移除 600 秒证据，不改变
`2a3e812` 的 sustained 实现或任何物理设备状态。

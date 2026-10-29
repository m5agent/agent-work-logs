# ESP-NOW external CCMP replay rejection 报告

## 背景

`0077` 已执行真实 AES-CCMP/MIC，但同一 authenticated encrypted datagram
如果被重复注入，仍可能再次通过 MIC 并到达 guest。目标是增加一个不依赖
host callback 的单 peer PN guard，并在真实 bridge 数据面制造一次 replay。

## 实现

- `Esp32WifiState` 保存 `espnow_peer_rx_pn_valid` 和
  `espnow_peer_last_rx_pn`，session realize/cleanup 与 wrapped key state
  一起重置。
- RX 先验证 CCMP/MIC；失败帧不能推进 counter。
- MIC 成功后，PN 等于或小于 last accepted PN 的帧在
  `espnow_peer_wrap_rx_envelope` 与 `Esp32_sendFrame` 之前丢弃。
- Python host 仍不构造 payload、MIC 或 guest callback。

## Replay 执行器

runner 的 `replay` scenario 在两侧 controller service ports 之间放置两个
UDP socket 作为透明 proxy。proxy 正常转发双向真实 action frame；只有
`left_to_right >= 2` 且 `right_to_left > 0` 后，才额外发送当前
left→right datagram 一次，避免在 peer 尚未 ready 时制造一个 lost frame。

结果：

| 项目 | 值 |
| --- | --- |
| left→right forwarded | `58` |
| right→left forwarded | `58` |
| replay sent | `true` |
| proxy errors | `0` |
| receiver TX/RX | `58/59` |
| receiver replay drops | `1` |
| receiver peer payload matches | `58` |

controller trace 顺序为正常 RX delivered、`RX drop: CCMP PN replay`、
后续正常 RX；重复帧没有进入 guest callback。

## 回归

| 场景 | 结果 |
| --- | --- |
| StopWatch↔StickS3 wrong-LMK | 双向 `EXPECTED_DROP`、`rx_packets=0` |
| Core2↔StopWatch encrypted | `15/44` source/payload matches |
| 6 sessions cleanup | terminal stopped、runtime PID gone、history retained、purge=0 |

## 构建与测试

- incremental QEMU build：PASS，SHA256
  `be7c376550829427b0fc72ada75f9d06e2246feaa64b2c222904d5a17a3c4076`
- `0078` forward/apply/source equality/reverse：PASS
- full platform suite：`1475 tests`，`OK (skipped=1)`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS
- GitHub CI：两个 job PASS

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU/patch hash 固定 |
| transport | `PASS` | transparent UDP proxy 转发真实 bridge datagram |
| data_behavior | `PASS` | 重复帧仅产生一次 controller replay drop |
| security boundary | `PASS` | MIC 失败不推进；authenticated equal/older PN drop-before-DMA |
| visual_or_physical | `NOT RUN` | 不覆盖 RF、电气、timing 或物理硬件 |
| multi-peer replay window | `NOT RUN` | 当前只实现单 peer monotonic guard |

## 验证边界

该 guard 是单 peer、顺序到达模型。它不处理多 peer replay window、
允许乱序的 window、PN wrap/key rotation、peer add/update/delete、
loss/retry、channel/rate、bit-exact controller、RF、AP coexistence、
电气时序或真机。

## 风险与回滚

bridge 仍为 default-off trusted-local fixture；普通 WiFi、HTTP、MQTT、
BLE 和物理设备路径不变。移除 `0078` 会恢复 `0077` 的 CCMP-only 行为；
主仓可整体 revert `cb689891` 回滚。没有执行不可逆硬件操作。

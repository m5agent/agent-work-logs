# Report

## 问题与目标

48-bit CCMP PN 不允许在同一 key 下静默复用。目标是在 PN 接近上限时验证
fail-closed，并确认普通 key-entry 重写不会伪造一次可接受 rekey；只有
实际 peer metadata/LMK 变化才能重启该 slot 的 PN 链。

## 实现

`0083-esp32-espnow-ccmp-pn-exhaustion.patch`：

1. 对 TX PN 增加 `0xffffffffffff` 上限检查；
2. 耗尽时记录 `CCMP PN exhausted` 并 drop，不编码 zero PN；
3. 增加 decimal 48-bit test seed，只应用于 slot 的第一次 PN 链；
4. metadata 开始写入时同时使 key entry 暂时 not-ready，避免旧 key 与新
   metadata 的混合状态；
5. 保存每个 slot 已发布的 metadata/LMK；
6. 相同 metadata/LMK 重写保持 TX PN 与 replay；
7. 只有实际变化才清 replay 并从 PN zero 开始。

runner 增加 `guest-key-pn-rekey` 和 `guest-key-pn-stale-rekey`。两个场景
都先完成 encrypted barrier，再发送 128 个 burn frame，随后分别安装新
LMK 或重写相同 LMK。

## 正控

最终 QEMU：
`1f3bb7dbbf4b2b32f29e065c02dbe20f08188518c01bd39ec5eb00c724574262`。

| role | TX/RX | key ready | exhaustion | replay drop | post payload |
| --- | ---: | ---: | ---: | ---: | ---: |
| StopWatch | 524/392 | 2 | 65 | 0 | 164 |
| StickS3 | 522/394 | 2 | 65 | 0 | 163 |

## Same-LMK 负控

重写相同 LMK 后，双方 key 仍有效，但 PN/replay 状态不被清除：

| role | TX/RX | exhaustion | replay drop | post payload |
| --- | ---: | ---: | ---: | ---: |
| StopWatch | 430/64 | 183 | 0 | 0 |
| StickS3 | 430/64 | 183 | 0 | 0 |

早期实现会在 metadata/key 写入开始就清 PN/replay，导致相同 LMK 也能恢复。
该行为被负控发现并修正；最终以已发布 key 快照比较，不按写事件猜测。

## 回归与清理

- shared-LMK 三 guest fabric：PASS；
- pairwise-LMK 三 guest fabric：PASS；
- B/A cross-wire negative：PASS；
- PN 正负控与上述三组回归共 13 个 session；
- 全部 `purge=0`、terminal stopped、PID gone、history retained。

## 检查

- ESP-NOW contracts：`51/51 PASS`；
- full platform：`1510` tests，`OK (skipped=1)`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS；
- compileall、new-contract Ruff 和 `git diff --check`：PASS；
- patch forward/current-source/reverse：PASS；
- CI `40823585571`：`platform-contracts` 与
  `network-namespace-policy` 均 PASS

## 未覆盖

- loss/retry、channel/rate、长稳；
- bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。

# Report

## 问题与目标

`RUNTIME-06` 已有 stock guest key、CCMP、replay、peer lifecycle、三 guest
fabric、per-peer key 和 PN exhaustion 路径，但缺少受控丢包、channel/rate
与更完整长稳。目标是在不替换 guest payload、CCMP、key 或 RX DMA 的前提下
补足 virtual link condition。

## 实现

`0084-esp32-espnow-loss-channel-rate.patch`：

1. bridge 增加 8-byte versioned envelope：magic、version、channel、rate、
   reserved；
2. channel 只允许 1–14，rate 只允许实际 802.11 whole-Mbps 集合；
3. RX 在 action/CCMP/DMA 前拒绝截断、错误 magic/version、超大 frame、
   异 channel 和不支持的 rate；
4. controller RX metadata 使用被交付 frame 的 envelope channel/rate；
5. runtime-env channel/rate 只能与 external peer bridge 组合；
6. runner 增加 `loss-retry`、`channel-match`、`channel-mismatch`、
   `rate-mixed` 和 `soak`。

envelope 位于 CCMP 外，是受信 test fixture。它不提供 authenticated
channel/rate security，也不模拟 RF propagation 或速率自适应。

## 失败 control

第一次 channel 正控只把 `add_peer(channel=6)` 用在仍连接 channel 1 AP 的
stock driver 上。guest 自身报告
`Peer channel is not equal to the home channel` 并拒绝发送。

最终探针先完成 Wi-Fi 基线，再 disconnect/re-activate STA 到目标 home
channel；这才是 stock ESP-NOW 的有效用户路径。

## 执行结果

| 场景 | 结果 | 数据 |
| --- | --- | --- |
| loss/retry | PASS | 左→右 drop 2；forwarded `56/58`；A/B 各 58 次发送 |
| channel 6↔6 | PASS | 两端 TX/RX `58/58`，channel drop 0 |
| channel 1↔6 | PASS negative | 两端各 40 drop，RX packet `0/0` |
| rate 11/24 Mbps | PASS | 两端 59 TX，互见对端 rate metadata |
| 60 秒 soak | PASS | A `528/527`，B `527/528`；matches `526/527` |

soak 的 duplicate payload、unexpected source 和 TX error 均为 0。

## 回归与清理

- direct encrypted guest-key pair：PASS；
- replay proxy：目标端 replay drop 1；
- reorder proxy：两端 replay drop 0；
- shared-LMK / pairwise-LMK 三 guest fabric：PASS；
- B/A cross-wire：只有 A↔B payload 归零；
- PN exhaustion/new-LMK rekey：两端各 65 次 exhaustion，post `166/164`；
- 27 个 session 全部 `purge=0`、stopped、PID gone、history retained。

## 检查

- platform：`1526 OK + 1 skipped`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS；
- compileall、Node contracts 和 `git diff --check`：PASS；
- patch forward/current-source/reverse：PASS；
- CI `40826797395`：`platform-contracts` 与
  `network-namespace-policy` PASS。

## 未覆盖

bit-exact controller/baseband、RF、天线、实测 channel/rate、电气和物理硬件。

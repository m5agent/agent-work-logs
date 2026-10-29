# ESP-NOW external CCMP replay window 报告

## 背景

`0078` 对 duplicate replay 正确，但严格 monotonic PN 会丢弃链路内合法乱序
帧。目标是在单 external peer 上增加 bounded authenticated window，同时
保持 duplicate 和超窗 old PN 拒绝。

## 实现

- state 新增 64-bit `espnow_peer_rx_pn_bitmap`；
- 首个 authenticated PN 设置 bit0；
- 更新 PN 时按差值左移 bitmap，差值 >=64 时清空；
- older PN 与 last 的差 >=64 丢弃；
- window 内未见 bit 接受并置位，已见 bit 丢弃；
- MIC 失败不推进 last/bitmap；
- realize/cleanup 与 wrapped key state 同步清零。

## 运行控制

`ReorderProxy` 在两方向均有流量后暂存一帧 left→right datagram；下一帧到达时
先发第二帧再发 held first frame。结果：

| 项目 | 值 |
| --- | --- |
| forwarded left→right | `58` |
| forwarded right→left | `58` |
| reordered | `true` |
| held frame released | `true` |
| proxy errors | `0` |
| receiver replay drops | `0` |

duplicate scenario 继续重复一帧；receiver RX 从 `58` 增至 `59` 并恰好记录
一次 `CCMP PN replay` drop。

## 回归

- StopWatch↔StickS3 reorder：peer payload `57/58`
- StopWatch↔StickS3 duplicate replay：drop `1`
- Core2↔StopWatch encrypted：payload `14/44`
- 六个 session 全部 `purge=0`、runtime PID gone、history retained

## 构建与测试

- incremental QEMU：PASS，SHA256
  `ef88746915960fe26a275cccfefcbb506cbc0f7d322747faad81a4a0916661cd`
- `0079` forward/source equality/reverse：PASS
- full platform suite：`1487 tests`，`OK (skipped=1)`
- generated checks：PASS
- GitHub CI：两个 job PASS

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU/patch hash 固定 |
| transport | `PASS` | 真实 UDP reorder proxy |
| data_behavior | `PASS` | 乱序两帧均接受，duplicate 仍拒绝 |
| security boundary | `PASS` | MIC 先于 window state |
| visual_or_physical | `NOT RUN` | 不覆盖 RF、电气、timing 或物理硬件 |
| multi-peer window | `NOT RUN` | 当前只实现单 peer |

## 验证边界

这不是 multi-peer replay window，也不覆盖 PN wrap、key rotation、
guest key-state 写入 QEMU bridge、loss/retry、channel/rate、bit-exact
controller、RF、AP coexistence、电气时序或真机。

## 风险与回滚

window 的 64-frame 大小是本模型的明确策略，不是从 datasheet 推导的
生产参数。回滚主仓 `1a90d3e6` 会恢复 `0078` 的严格 monotonic guard。
bridge 仍默认关闭并使用 trusted-local fixture。

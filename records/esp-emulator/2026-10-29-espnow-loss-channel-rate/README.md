# ESP Emulator ESP-NOW loss/retry, channel/rate and soak

- 日期：`2026-10-29`
- 结果：`PASS`（virtual-device）；bit-exact controller、RF 和物理硬件 `NOT RUN`
- 工作类型：`code_change`
- 问题来源：`RUNTIME-06` 的 loss/retry、channel/rate 与长期稳定性
- Base：`7449da2af2ea4c7a77735e79cf4a541fd64e9967`
- 结果提交：`6c72ea74ebfe4fd64770ced888012900d3bb2cde`
- 环境：macOS arm64；真实 QEMU guest；stock UIFlow2 `v2.5.3`；
  StopWatch/StickS3/Core2 virtual-device

## 结论

`0084` 在真实 ESP-NOW action frame 外增加 8-byte、带版本号的 channel/rate
envelope。RX 在 action/CCMP/DMA 前拒绝截断、错误 magic/version、异 channel
和不支持的 rate。该 envelope 是受信 test fixture、位于 CCMP 外，不作为
authenticated security field。

受控 proxy 丢弃 StopWatch→StickS3 前两帧后，应用重试恢复双向 payload。
channel 6 正控 PASS；channel 1↔6 两端各 40 次 drop、正常 RX packet 为 0。
11/24 Mbps 混合发送时，接收端 metadata 互见对端 rate。60 秒 soak 中
A/B TX/RX 为 `528/527` 与 `527/528`，payload matches 为 `526/527`，
duplicate、unexpected source 和 TX error 均为 0。

direct encrypted、replay、reorder、三 guest shared/pairwise fabric、
cross-wire 和 PN exhaustion/new-LMK rekey 均保持。`RUNTIME-06` 的
virtual-device 边界关闭。

## 关键证据

- QEMU SHA256：
  `54e7a7f7cd0ff6f5a1d6343c06563388f49c2b0abbca4cafb850876e57ed1254`
- `0084` patch SHA256：
  `91ef766541a9802336d5a3efaefc38fd28f5d7ea55107e605e2ec37fdf2594fc`
- runner SHA256：
  `f0416d4d2acc396a49a830d507530145af07111563cc8e0184623c4d2c535ef2`
- loss proxy：drop `2`，forwarded `56/58`；
- channel mismatch：两端各 `40` drop，正常 RX `0/0`；
- soak：60 秒、两端合计超过 1000 次 TX/RX、无重复/非法来源；
- 27 个最终 session：`purge=0`、stopped、PID gone、history retained；
- platform：`1526 OK + 1 skipped`；
- GitHub CI：[40826797395](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40826797395)
  `platform-contracts` 与 `network-namespace-policy` PASS；
- 主仓证据：
  [ESP-NOW loss/channel/rate](https://github.com/m5agent/m5stack-esp-emulator/blob/6c72ea74ebfe4fd64770ced888012900d3bb2cde/docs/evidence/2026-10-29-espnow-loss-channel-rate/README.md)。

## 文件

- `report.md`：实现、负控、回归、检查和边界
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：forward/current/reverse patch 验证
- `patches/0001-esp32-espnow-loss-channel-rate.patch`：`0084` 原样 patch
- `patches/README.md`：patch 应用范围与校验命令

## 未覆盖项

- bit-exact controller/baseband；
- RF propagation、天线、实测 channel/rate 和速率自适应；
- 电气时序；
- physical hardware validation。

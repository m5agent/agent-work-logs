# Report

## 问题与目标

前序 `0076`–`0080` 已证明两个 independent guest 的 plaintext/CCMP、
单 peer replay window 和 stock guest controller key-state。目标是把同一
真实 controller 数据面扩展到三个 guest，并让每个 receiver 对多个 source
peer 分别维护 authenticated replay state。

本轮使用 shared LMK，只关闭多 guest fabric 和 per-source replay；不同
peer 使用不同 LMK 的 key routing 不在本轮范围内。

## 根因与失败控制

首个实现先在 guest CCMP 后改写 transmitter/address3，broker 转发前又改写
一次。两个地址字段属于 CCMP AAD，MIC 计算后修改会使所有接收端验证失败。
该实现被拒绝，没有进入最终结果。

最终设计在 guest 加密前写入每个 controller 自己的 synthetic public
identity，broker 只按 source/receiver 路由，并在 MIC 后保留这条身份。
receiver 因此在验证 MIC 后用稳定的 source-peer identity 选择 replay slot。

早期 readiness 使用单独的两阶段 barrier；Core2 尚未 ready 时，另外两个
guest 已结束交换。最终 runner 将 READY 和持续 payload 交换放在同一个
24 秒循环内，positive 和 replay 负控都用该版本重跑。

## 改动

`0081-esp32-espnow-peer-fabric.patch`：

1. 增加 opt-in `M5SW_ESPNOW_PEER_FABRIC=1` 和 synthetic public identity；
2. transmitter/address3 在 CCMP 前确定，broker 不再于 MIC 后改写；
3. RX 保留 broker-supplied source peer；
4. replay state 按 source-peer 分为 8 个 slot，每 slot 为 64-frame bitmap；
5. MIC 验证先于 replay state 查询，失败帧不推进 window；
6. key clear/replacement、reset 和 cleanup 清理全部 peer window。

Device Service 只允许 fabric 与 external bridge 组合，拒绝 PMK/LMK
fixture 混用和非法 public identity；private runtime env 继续从 snapshot
与持久记录中脱敏。

runner 新增 `fabric` 和 `fabric-replay`，使用同一 broker 连接三个真实
guest session。负控只对目标 receiver 断言一次 drop；任何 A/C drop 或目标
不为 `1` 都会使结果 FAIL。

## 执行与证据

最终 QEMU binary：
`de8d5b07a31861bf3aae0731ad21da772753cb1bd1388f5b678bdcf23a0ef9b1`。

| 场景 | StopWatch TX/RX | StickS3 TX/RX | Core2 TX/RX | replay drop |
| --- | ---: | ---: | ---: | --- |
| 三 guest 正控 | 844/854 | 828/862 | 880/352 | `0/0/0` |
| replay 负控 | 848/870 | 844/873 | 896/346 | `0/1/0` |

三端 `peer_count` 均为 `[2,2]`；每端都收到另外两个 peer 的正确 payload。
broker 观察到全部六个 directed path，错误为 `0`。

六个 session 均使用 `purge=0` 停止，terminal `stopped`、runtime PID
gone、history retained。最终 runner 的 replay 判定还要求
`history_preserved=true`。

## 检查

- ESP-NOW controller/patch contracts：`42/42 PASS`；
- Device Service：`123/123 PASS`；
- full platform：`1501` tests，`OK (skipped=1)`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS；
- compileall、new-contract Ruff 与 `git diff --check`：PASS；
- CI `40817584295`：`platform-contracts` 与
  `network-namespace-policy` 均 PASS

## 兼容性与回滚

未设置 `M5SW_ESPNOW_PEER_FABRIC` 时，双 guest external bridge 保留原有
地址兼容路径。回滚 `0081` 和 runner fabric scenarios 即可恢复 `0080` 的
单 peer guest-key 行为。

## 未覆盖

- per-peer LMK routing、错误 peer-key 路由；
- PN wrap、loss/retry 和更完整 key lifecycle；
- channel/rate、bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。

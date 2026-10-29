# ESP Emulator three-guest shared-LMK ESP-NOW fabric

- 日期：`2026-10-29`
- 结果：`PASS`（限定三 guest shared-LMK virtual-device fabric）
  / `PARTIAL`（`RUNTIME-06` 总体）
- 工作类型：`code_change`
- 问题来源：`RUNTIME-06` 的三 guest action-frame fabric、per-source replay
  window 和 replay 负控
- Base：[m5stack-esp-emulator@96ee9f33](https://github.com/m5agent/m5stack-esp-emulator/commit/96ee9f33a55a565f45a72315d29a91993f69cd46)
- 结果提交：[m5stack-esp-emulator@75d66458](https://github.com/m5agent/m5stack-esp-emulator/commit/75d66458a4e658abbdba945fc24da0fea2c4eb64)
- 环境：macOS arm64；QEMU virtual device；stock UIFlow2 `v2.5.3`

## 结论

`0081` 将 `0080` 的 stock guest controller key-state 扩展到 StopWatch、
StickS3 和 Core2 三 guest fabric。每个 controller 在 CCMP 前使用自己的
synthetic public identity，broker 在 MIC 后不改写受 AAD 保护的地址；RX
replay window 按 authenticated source-peer 分片，共 8 个 slot、每 slot
64 frame。

三方正控均由正常 controller TX/RX DMA 收到另外两个 peer 的 payload。
replay 负控复制一帧真实 forwarded frame 后，目标 StickS3 精确记录
`replay_drops=1`，StopWatch/Core2 精确为 `0`，正常 payload 保持。

全部为 **virtual-device validation**。`RUNTIME-06` 仍为 `PARTIAL`：
per-peer LMK routing、PN wrap、loss/retry、channel/rate、bit-exact
controller、RF、电气和真机仍为 `NOT RUN`。

## 关键证据

- QEMU SHA256：`de8d5b07a31861bf3aae0731ad21da772753cb1bd1388f5b678bdcf23a0ef9b1`
- `0081` patch SHA256：`b86d3561d503139a4ae8dbda6c4699534b478113ff681784012e562d4d8cf7ca`
- runner SHA256：`74429e26440c7bbce6c2ad47ef99b03939c1ab62db5daf21da9350dc07e24d97`
- 三端 `peer_count=[2,2]`，各自收到另外两个 peer 的 payload
- replay 负控：目标 B `1`、A/C `0`；runner 对该 `1/0/0` 做严格断言
- 六个 session 全部 `purge=0`、terminal `stopped`、PID gone、
  history retained
- platform tests：`1501 OK + 1 skipped`
- patch：forward、current-source equality 和 reverse 均 PASS
- GitHub CI：[40817584295](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40817584295)：
  `platform-contracts` 与 `network-namespace-policy` 均 PASS
- 主仓证据：[peer fabric](https://github.com/m5agent/m5stack-esp-emulator/blob/75d66458a4e658abbdba945fc24da0fea2c4eb64/docs/evidence/2026-10-29-espnow-peer-fabric/README.md)

## 文件

- `report.md`：实现、失败控制、执行、边界和回滚
- `run.json`：机器可读记录
- `evidence/summary.json`：脱敏 machine summary
- `evidence/patch-check.txt`：patch apply/current/reverse 验证
- `patches/0001-esp32-espnow-peer-fabric.patch`：`0081` 原样 patch
- `patches/README.md`：patch 与 preimage 校验说明

## 未覆盖项

- per-peer LMK routing 和错误 peer-key 路由负控；
- PN wrap、loss/retry 和更完整 key lifecycle；
- channel/rate、bit-exact controller；
- RF、antenna、电气、timing 和 physical hardware。

# native ESP-NOW peer lifecycle 报告

## 背景

`0077`/`0078` 已验证 external encrypted payload、错误 LMK 和单 peer replay，
但尚未证明 stock guest 的 peer add/delete/modify 生命周期。目标是用原厂
`espnow.ESPNow` API 完成可观察的创建、删除、删除后发送拒绝、修改、重加和
恢复传输，同时保持正常 controller TX/RX DMA 路径。

## API 依据

本机 UIFlow2 MicroPython 官方 `espnow.rst` 定义：

- `add_peer(mac, lmk, channel, ifidx, encrypt)`；
- `del_peer(mac)`；
- `get_peer(mac)` 返回 `(mac, lmk, channel, ifidx, encrypt)`；
- `peer_count()` 返回 `(peer_num, encrypt_num)`；
- `mod_peer(...)` 修改已注册参数；
- `send()` 对未注册 peer 抛 `ESP_ERR_ESPNOW_NOT_FOUND`。

runner 只用这些公开接口，不直接查看 QEMU controller state。

## 执行流程

1. Wi-Fi fixture 连接后初始化 `espnow.ESPNow()`；
2. `set_pmk` 和 encrypted `add_peer`，检查 `[1,1]`；
3. 每侧发送 role-specific PRE marker，直到看到 peer PRE；
4. 第一次看到 PRE 后再持续广播 1.5 秒，给较慢 Core2 完成双向屏障；
5. `del_peer` 并检查 `[0,0]`、`get_peer` NOT_FOUND、`send` 被拒；
6. 重新 `add_peer` 和 `mod_peer`，检查 `[1,1]` 及 encrypt 属性；
7. 发送 POST marker 并等待 peer POST，证明生命周期后传输恢复。

## 结果

| 设备对 | 设备 | bridge TX/RX | initial | deleted | readded | result |
| --- | --- | ---: | --- | --- | --- | --- |
| StopWatch↔StickS3 | StopWatch | 16/16 | `[1,1]` | `[0,0]` | `[1,1]` | PASS |
| StopWatch↔StickS3 | StickS3 | 16/16 | `[1,1]` | `[0,0]` | `[1,1]` | PASS |
| Core2↔StopWatch | Core2 | 51/35 | `[1,1]` | `[0,0]` | `[1,1]` | PASS |
| Core2↔StopWatch | StopWatch | 39/51 | `[1,1]` | `[0,0]` | `[1,1]` | PASS |

四个 session 的 `get_peer_not_found`、`send_rejected`、`modified`、
`pre_synced`、`post_resumed` 全为 true。

## Failure control

最初 Core2 pair 中 StopWatch 收到 Core2 PRE 后立即删除 peer，而启动较慢的
Core2 尚未看到回向 PRE：Core2 `pre_synced=false`，StopWatch 为 true。
delete/re-add/modify 本身两边均 PASS。runner 改为首次匹配后继续广播 PRE
1.5 秒再删除，随后两个设备对均 PASS。该竞态属于 runner 屏障，不是 QEMU
peer 操作失败。

## 构建与测试

- QEMU 未再次修改；使用 SHA256
  `be7c376550829427b0fc72ada75f9d06e2246feaa64b2c222904d5a17a3c4076`
- full platform suite：`1479 tests`，`OK (skipped=1)`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS
- GitHub CI：两个 job PASS

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| transport | `PASS` | 独立 guest 经正常 controller TX/RX DMA |
| device_response | `PASS` | 原生 add/del/get/modify/peer_count |
| data_behavior | `PASS` | delete 后发送拒绝，re-add 后双向传输恢复 |
| guest key-state → QEMU bridge | `NOT RUN` | bridge key 仍来自 explicit fixture |
| visual_or_physical | `NOT RUN` | 不覆盖 RF、电气、timing 或物理硬件 |

## 验证边界

这是 stock native API 生命周期，不证明 QEMU bridge 读取了 guest PMK/LMK，
也不覆盖 key rotation、m5espnow wrapper、多 peer replay window、
loss/retry、channel/rate、bit-exact controller、RF、AP coexistence、
电气时序或真机。

## 风险与回滚

bridge 仍为 trusted-local、default-off fixture。回滚主仓
`ccd23e41` 会移除 lifecycle scenario 和文档，不影响既有 encrypted/replay
lane。没有执行不可逆硬件操作。

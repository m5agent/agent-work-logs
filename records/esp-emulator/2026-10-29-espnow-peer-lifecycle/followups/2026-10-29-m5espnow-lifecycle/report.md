# M5ESPNow wrapper lifecycle 报告

## 背景

native `espnow.ESPNow` peer lifecycle 已验证后，仍需覆盖原厂
`m5espnow.M5ESPNow` wrapper。wrapper 使用 peer-id、hex MAC/string key 和
peer-list 管理，delete 后发送路径也与 native 不同。

## API 与执行

runner 使用官方 wrapper API：

- `M5ESPNow(0)`；
- `set_pmk_encrypt(PMK)`；
- `set_add_peer(peer_mac_hex, 1, 0, True, LMK)`；
- `peer_count()` / `get_peer_list(1)`；
- `set_delete_peer(1)`；
- `send_data(1, payload)` / `recv_data(timeout_ms)`；
- `deinit()`。

每侧先发送 role-specific PRE marker，第一次看到 peer PRE 后继续广播 1.5 秒，
以避免 Core2 启动差异造成单向屏障。随后删除 peer、检查 list/count、
执行 delete 后 `send_data` no-op，再重新注册并等待 POST 与双向 payload。

## 结果

| 设备对 | 设备 | bridge TX/RX | initial | deleted | readded | result |
| --- | --- | ---: | --- | --- | --- | --- |
| StopWatch↔StickS3 | StopWatch | 15/15 | `[1,1]` | `[0,0]` / `[]` | `[1,1]` | PASS |
| StopWatch↔StickS3 | StickS3 | 15/15 | `[1,1]` | `[0,0]` / `[]` | `[1,1]` | PASS |
| Core2↔StopWatch | Core2 | 21/32 | `[1,1]` | `[0,0]` / `[]` | `[1,1]` | PASS |
| Core2↔StopWatch | StopWatch | 33/21 | `[1,1]` | `[0,0]` / `[]` | `[1,1]` | PASS |

所有 session 的 deleted peer list empty、send-after-delete no-op、peer-list
restored、pre/post sync 均 true。

## 构建与测试

- QEMU 未再修改，SHA256
  `be7c376550829427b0fc72ada75f9d06e2246feaa64b2c222904d5a17a3c4076`
- full platform suite：`1481 tests`，`OK (skipped=1)`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS
- GitHub CI：两个 job PASS

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| transport | `PASS` | wrapper 经正常 controller TX/RX DMA |
| device_response | `PASS` | add/delete/get_peer_list/peer_count/re-add |
| data_behavior | `PASS` | delete 后 no-op，re-add 后双向传输恢复 |
| guest key-state → QEMU bridge | `NOT RUN` | bridge key 仍为 explicit fixture |
| visual_or_physical | `NOT RUN` | 不覆盖 RF、电气、timing 或物理硬件 |

## 验证边界

这是 wrapper API 生命周期，不证明 QEMU bridge 读取 guest PMK/LMK，也不覆盖
key rotation、多 peer replay window、loss/retry、channel/rate、bit-exact
controller、RF、AP coexistence、电气时序或真机。

## 风险与回滚

bridge 仍为 trusted-local、default-off fixture。回滚主仓 `398509e9`
会移除 wrapper scenario 和文档，不影响 native lifecycle、CCMP 或 replay lane。
没有执行不可逆硬件操作。

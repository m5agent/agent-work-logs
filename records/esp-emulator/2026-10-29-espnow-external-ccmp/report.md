# ESP-NOW external peer key-bound CCMP 报告

## 背景

`0076` 已让两个独立 guest 经正常 controller TX/RX DMA 交换未加密 ESP-NOW
management action frame，但 guest hardware CCMP envelope 本身不足以证明
bridge 使用 peer LMK 加密和验证 payload。最初把该 envelope 原样跨 controller
搬运时，即使两侧配置不同 LMK，双向 payload 仍然 PASS；因此该实现被拒绝。

目标是增加可重放的 key-bound CCMP 正负控，同时确保 PMK/LMK 不进入
持久化 session 或 API snapshot。

## 实现

- `M5SW_ESPNOW_PEER_PMK` / `LMK` 必须成对提供，各为 32 个十六进制字符；
  只能与成对 external peer ports 使用。
- PMK 以 AES-128-ECB wrap LMK；controller state 只保留 PMK 和 wrapped LMK。
- TX 移除 closed driver 的 hardware envelope，临时 unwrap LMK，再以 fresh PN
  和 8-byte MIC 执行 AES-CCMP。
- RX 解析 PN、unwrap LMK 并验证 AAD/plaintext/MIC；失败时在
  `Esp32_sendFrame` 前 `continue`，不会进入 guest DMA 或 callback。
- PMK/LMK 在 API snapshot 与 persisted session JSON 中显示为
  `<redacted>`；进程仍需原始 fixture key，但 raw generated guest source 只保留
  在 ignored 本地运行目录。
- 新 patch 为 `0077-esp32-espnow-external-ccmp.patch`，默认关闭语义仍由
  `0076` 的 external port pair 控制。

## 执行结果

| 场景 | 设备对 | peer payload | 预期 | 结果 |
| --- | --- | ---: | --- | --- |
| plaintext | StopWatch↔StickS3 | `57` / `58` | PASS | PASS |
| encrypted | StopWatch↔StickS3 | `58` / `57` | PASS | PASS |
| wrong-LMK | StopWatch↔StickS3 | `0` / `0` | DROP | EXPECTED_DROP |
| wrong-PMK, same LMK | StopWatch↔StickS3 | `58` / `57` | PASS | PASS |
| encrypted | Core2↔StopWatch | `15` / `44` | PASS | PASS |
| wrong-LMK | Core2↔StopWatch | `0` / `0` | DROP | EXPECTED_DROP |

wrong-LMK 场景仍观察到 bridge TX/RX traffic，说明帧已到达 peer controller，
但 CCMP 验证失败后才被丢弃。wrong-PMK/same-LMK 继续通信符合 ESP-NOW 语义：
PMK 只保护本地保存的 LMK，on-wire key 是 LMK。

12 个独立 session 路径的 terminal state 均为 `stopped`，
`runtime_pid_gone=true`，使用 `purge=0` 并保留 evidence/history。

## 代码与构建检查

- incremental QEMU build：PASS；输出 SHA256
  `5340171ca484ce7ee3b13a0538a35c5f22fcd3a2ff726fa7a902424ff4d7d179`
- `0077` forward apply check：PASS
- applied files 与 recorded QEMU source 逐文件 `cmp`：PASS
- reverse apply check：PASS
- full platform suite：`1470 tests`，`OK (skipped=1)`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  PASS
- GitHub CI：两个 job PASS

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU binary hash 与 patch checksum 固定 |
| transport | `PASS` | 两个独立 controller 的正常 TX/RX DMA 路径 |
| device_response | `PASS` | stock UIFlow2 ESP-NOW registration/send/recv |
| data_behavior | `PASS` | 正确 key payload 匹配；wrong-LMK 零 guest payload |
| security boundary | `PASS` | PMK/LMK API/persistence redaction；MIC failure drop-before-DMA |
| visual_or_physical | `NOT RUN` | 不覆盖 RF、antenna、electrical、timing 或 physical hardware |
| guest key lifecycle | `NOT RUN` | key fixture 由 controller boundary 显式提供，非 guest state 读取 |

## 验证边界

该 lane 是 explicit key fixture，不证明 guest `set_pmk` 或 encrypted
`add_peer` 已把 key-state 写入 controller。它也不证明 key rotation、
peer add/update/delete、replay protection、loss/retry、双 peer 以上 fabric、
channel/rate、bit-exact controller、RF、AP coexistence、电气时序或真机。

## 风险与回滚

未执行物理烧录或不可逆硬件操作。bridge 仍为 trusted-local、默认关闭
fixture；普通 WiFi association、DHCP、HTTP、MQTT 和 BLE 路径不变。
移除 `0077` 会恢复 `0076` 的明文 baseline，并关闭 encrypted/CCMP lane；
主仓可整体 revert `82118424` 回滚。

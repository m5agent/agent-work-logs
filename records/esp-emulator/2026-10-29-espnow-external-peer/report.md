# ESP-NOW 外部明文 peer 报告

## 背景

已有的 `0067` 只验证同一 guest 内的 controller loopback，无法证明两个
独立 emulated guest 能从正常 TX DMA 发出 action frame，再由另一
controller 的正常 RX DMA 接收。`RUNTIME-06` 因此继续保持 `PARTIAL`。

目标是先完成最小、可审计的 external plaintext exchange，并把 loopback、
external 和 encrypted lane 分开记录。

## 结论

新增默认关闭的 `0076-esp32-external-espnow-peer-bridge.patch`。只有两侧
同时配置成对的 host-local UDP 端口时才启用；bridge：

- 只转发 802.11 management action frame；
- 保留 guest 正常 controller TX/RX DMA 路径；
- 把发送端身份绑定当前 controller 的 session MAC；
- 拒绝残缺端口、相同端口和与 `0067` 同 guest loopback 混用；
- 不向 guest 注入 Python payload 或直接调用 callback。

StopWatch↔StickS3 与 Core2↔StopWatch 两对独立 session 均 PASS。

## 执行

| 项目 | 值 |
| --- | --- |
| Runtime | `qemu-wifi` |
| QEMU SHA256 | `df0e20f176494a9de8e32361dbc865688c5e72791207793d0bdb0b5a947b616a` |
| Patch SHA256 | `de39dd922d15bc2ad3827a13293d86dc2a2f0dafcfe2036783730dfab8037c62` |
| Runner SHA256 | `a5bfcb7a7a1a88a64c3464a1ac7437a0b78080b887b0d86e5305918faedd780a` |
| Scenario | `plaintext`; `encrypt=False`; 12-second bounded exchange window |
| StopWatch↔StickS3 | `57/57` and `58/58` source/payload matches |
| Core2↔StopWatch | `14/14` and `44/44` source/payload matches |

Core2 的 UIFlow2 网络初始化明显慢于 S3。先前的 4 秒窗口在 Core2 开始
收包前结束，保留为 harness control；最终 runner 使用 12 秒有界窗口，
同时持续发送和接收，避免把启动延迟写成协议失败。

## 证据

- bridge/default-off/port-pair contract：`6/6 PASS`
- Device Service unit suite：`123/123 PASS`
- final platform suite：`1440` 项，`OK (skipped=10)`
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`
- patch scope：`PASS`，16 blobs，evidence 8,756 bytes
- 四个 session：terminal `stopped`、`runtime_pid_gone=true`、
  `history_preserved=true`
- 原始 serial/frame/ZIP 只在被忽略的本地运行目录；记录仓只保留脱敏
  [summary.json](evidence/summary.json)

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | final QEMU SHA 与 patch checksum 固定 |
| transport | `PASS` | 两个独立 guest 通过正常 controller TX/RX DMA 交换 action frame |
| device_response | `PASS` | 原厂 `espnow.ESPNow` registration、send、recvinto |
| data_behavior | `PASS` | source identity 和 role payload 逐包匹配 |
| visual_or_physical | `NOT RUN` | 不覆盖 RF、天线、电气、channel/rate 或 timing |
| encrypted ESP-NOW | `NOT RUN` | 无 PMK/LMK/CCMP 实现或错误-key 负控 |

## 验证边界

本次只证明两个独立 guest 的未加密 action-frame exchange。它不证明
PMK/LMK/CCMP、错误 key、peer add/update/delete、replay、loss/retry、
超过两个 peer 的 fabric、bit-exact controller、RF、AP 共存、电气时序或
物理硬件。

## 风险与回滚

未执行物理烧录或不可逆设备操作。bridge 默认关闭，只接受 trusted-local
fixture 配置；不会改变普通 WiFi association、DHCP、HTTP 或 MQTT。
移除 `0076` 会恢复 external peer lane 为不可用，不影响 `0067` 同 guest
loopback。主仓整体可用 revert 本次结果 commit 回滚。

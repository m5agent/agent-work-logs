# ESP-NOW loopback 与三设备接口最终复测报告

## 背景

用户要求在当前最新模拟器上重新并发测试 StopWatch、StickS3 和 Core2 的
UIFlow2 接口，统一收集失败后再处理。上一轮已确认 Core2 legacy `RUNTIME-03`
仍未闭环，ESP-NOW 只有 state/peer table，controller payload 和 IRQ 为
`BLOCKED_MODEL`。

## 结论

普通 UIFlow2 system、协议、音频和设备组路径在三台均未发现新的模拟器回归。
两个值得处理的测试/模型问题为：

1. `audio.Player.play_tone(sync=True)` 的 stock 实现会在返回后短暂保持
   `RUNNING`，约 1.5–2 秒后进入 `FINISHED`；旧 probe 在返回瞬间采样，
   形成测试竞态。
2. ESP-NOW action frame 被 OpenMAC management dispatcher 丢弃。新增
   opt-in controller loopback 后，stock guest 通过真实 TX/RX DMA 完成
   payload、receive 和 IRQ。

## 根因与改动

### audio wrapper 采样竞态

最小 probe 每秒轮询状态。`play_tone` 返回时状态为 `RUNNING(1)`，约
1.5–2 秒后状态回调进入 `FINISHED(4)`。probe 改为最多 3 秒的有界等待，
没有修改 guest 或 QEMU audio 行为。

### ESP-NOW controller loopback

`0067-esp32-espnow-controlled-peer-loopback.patch` 只在
`M5SW_ESPNOW_LOOPBACK=1` 时：

- 接收 guest 经正常 TX DMA 写出的 management action frame；
- 交换 receiver/transmitter 地址并从正常 RX DMA 送回；
- broadcast echo 使用固定 locally-administered fixture peer；
- 非 action frame、非 management frame 和其他 runtime 路径保持原状。

Device Service allowlist 增加同一显式环境变量；protocol runner 把 fixture
状态写入 `protocol-results.json`，避免把 loopback 结果误写外部 peer PASS。

## 执行

- final QEMU SHA256：
  `c3c3140322513de6f3ef724513e2f1272764e6af8a8fdd7c7bfd4448dc17f534`
- QEMU compile：`ninja -C .work/M5StopWatch-QEMU/build/qemu/build
  qemu-system-xtensa`
- 三设备 system/shared：六个独立可见 session 并发
- 三设备设备组：三个 `run_peripheral_matrix.py --device` 并发
- protocol/audio/TLS：通过 `/api/v1` session、evidence ZIP、`purge=0`
- 最终 QEMU、Device Service 和协议 runner 进程全部清理

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | final QEMU 增量编译；`0067` reverse apply |
| transport | `PASS` | TX/RX DMA serial、evidence ZIP、pcap、PCM |
| device_response | `PASS` | system/shared/device groups、ESP-NOW peer echo |
| data_behavior | `PASS` | exact payload/MAC、IRQ、PCM、TCP/UDP/MQTT bytes |
| visual_or_physical | `PARTIAL` | frame/device-group oracle PASS；物理视觉/声学 `NOT RUN` |
| external ESP-NOW peer | `NOT RUN` | 当前只有同 guest loopback |

## 验证边界

本轮不证明外部 ESP-NOW peer、PMK 加密 payload、跨设备 fabric、loss/retry、
channel/rate、RF/antenna 或电气时序。Core2 legacy `RUNTIME-03` 仍为 `OPEN`。
所有结论都是虚拟设备结果。

## 风险与回滚

未执行物理烧录或不可逆设备操作。`0067` 默认关闭；移除 patch 会恢复
ESP-NOW payload/IRQ 的 `BLOCKED_MODEL`，不影响现有 WiFi association、
DHCP、HTTP 或 MQTT 路径。主仓整体回滚为 revert 本次修复 commit。

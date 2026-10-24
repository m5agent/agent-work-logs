# ESP Emulator S3 WPA2-PSK 数据面

- 日期：`2026-10-25`
- 结果：`PASS`（accepted virtual-device scope）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`3f4bf92b96d5854f0804d7f7014c4a9c244da99e`
- 结果版本：`08d8a21bda173ff65dfb5343d0fa8082732eb872`
- 环境：macOS Apple Silicon；QEMU `9.2.2`/`da100c9` patched worktree；Device Service

## 结论

ESP32-S3 QEMU AP 从仅支持 Open auth 扩展为可验证的 WPA2-PSK 路径：
beacon/probe/association 广告 RSN，正确密码完成 M1-M4、PTK/GTK、CCMP RX、
DHCP、`api.openai.com` DNS 和 TCP/443；错误密码在 M2 MIC 被拒绝、
deauthenticate 后重试且无 DHCP。

Station eFuse 与 QEMU NIC 现在由 session id 派生同一 synthetic MAC。S3 RX
模型验证 CCMP 后向 closed WiFi firmware 提供其 hardware-decrypted 布局；
DHCP reply 以 pairwise-key 802.11 unicast 交付，不绕过 guest 网络栈。

## 关键证据

- OpenAI BIN SHA256：
  `b3597fcabbff57c98618caa8754af84745e9eac35b2868ab3c4cb0935b7c59b3`
- Device Service 三组 Open/WPA2/错误密码 investigation checks：`22/22 PASS`
- 正确密码 pcap：`38` packets、DNS `api.openai.com.`、TCP/443 flow `1`
- 错误密码：无 association、无 DHCP、无 HTTP，pcap `0` packets
- QEMU patch predecessor-stack forward/reverse round-trip：`PASS`（不是裸上游单补丁）
- AtomS3R/StickS3/CoreS3 定向外设矩阵：`15/15 PASS`、无 retry
- 平台测试 `377/377`，文档契约 `20/20`，Node `2/2`
- GitHub Actions：`platform-contracts` 与 `network-namespace-policy` 均 `PASS`：
  `https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40138447697`

## 文件

- `report.md`：根因、修复、验证和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合证据；
- `patches/0029-esp32s3-wpa2-psk-data-plane.patch`：可重放 QEMU patch。

## 未覆盖项

- WPA3-SAE；
- WPA2 group-key multicast；
- 真实 RF/PHY、channel/rate、roaming、干扰与功耗；
- 真实 OpenAI 凭据、Realtime/WebRTC 音频和云端业务成功；
- physical hardware validation。

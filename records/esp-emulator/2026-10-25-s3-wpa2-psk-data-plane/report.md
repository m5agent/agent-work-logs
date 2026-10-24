# ESP Emulator S3 WPA2-PSK 数据面报告

## 背景

公开 OpenAI Voice Assistant AtomS3R 固件从 NVS 读取非空密码后，把 WiFi
authmode threshold 从 Open 提升到 WPA2。旧 QEMU S3 AP 只广播 Open auth，
因此 guest 持续 retry，不能 association、DHCP 或访问 HTTPS。

本任务的目标不是让主机侧直接返回“已连接”，而是补齐固件实际使用的 RSN、
EAPOL、CCMP、MAC、DMA 和 DHCP 数据路径，并以公开固件 SHA 绑定结果。

## 根因与修复

发现三个独立缺口：

1. AP 没有 WPA2 RSN/EAPOL 状态机；
2. guest supplicant、S3 eFuse 和 QEMU NIC 的 station address 不一致；
3. 广播 DHCP reply 进入 guest 的 group-key 路径，而 closed firmware 的
   group key 未安装，数据帧在 guest callback 前被丢弃。

修复：

- beacon、probe response 和 association response 广告 WPA2-PSK/CCMP RSN；
- 从 SSID/password 派生 PMK，由 M1/M2 nonce 与 STA/BSSID 派生 PTK；
- 发送 M1/M3，验证 M2/M4 MIC；错误密码发送 reason 15 deauth；
- 为 host 网络侧帧生成真正的 AES-CCM/CCMP 数据；
- S3 radio RX 使用 PTK/GTK 验证 CCMP，再把 LLC 明文和原 CCMP header 组合
  成 closed firmware 期望的 hardware-decrypted RX 布局；
- 每次 session 从 session id 派生 locally-administered MAC，同时写入 S3
  eFuse fixture 与 QEMU NIC；
- 对安全连接中的 DHCP reply 采用 802.11 单播 receiver，帧内以太网 payload
  仍由 guest DHCP 栈处理；
- 服务 API 接受 `wifi_auth=open|wpa2-psk`，WPA3-SAE 返回
  `unsupported_wifi_security`。

QEMU 修复提交为 `patches/qemu-m5stack-peripherals/0029-esp32s3-wpa2-psk-data-plane.patch`。
该补丁依赖前面已导入的 S3 WLAN/MAC 和双 guest fabric 系列，不是可单独应用到
裸上游 `da100c9` 的独立快照；补丁 round-trip 已在对应的 predecessor-patched
worktree 状态验证。

## 执行

通过 Device Service 对同一公开 BIN SHA 运行三组 session：

- Open AP + 空密码 NVS；
- WPA2-PSK AP + 正确密码 NVS；
- WPA2-PSK AP + 错误密码 NVS。

每组使用 session-isolated NVS overlay，源 firmware 和 NVS artifact 均不改写。

本地验证：

```text
platform tests                 377/377 PASS
documentation contracts        20/20 PASS
Node upload/SHA                2/2 PASS
OpenAI probe checks            22/22 PASS
S3 targeted matrix             15/15 PASS
QEMU patch forward/reverse     PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
project snapshot               PASS
git diff --check               PASS
```

正确密码 session：

```text
EAPOL 1/4 sent
EAPOL 2/4 verified
EAPOL 3/4 sent
EAPOL 4/4 verified; WPA2-PSK ready
CCMP RX decrypted
wifi:connected with myssid
got ip:<redacted>
api.openai.com DNS + TCP/443
```

错误密码 session：

```text
EAPOL 2/4 MIC mismatch
deauthenticate station reason=15
retry to connect to the AP
no associated marker
no DHCP
no HTTP
pcap packets=0
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | patched QEMU binary built; patch applies both directions on the declared predecessor stack |
| flash | `PASS` | Device Service validated complete S3 image and session-isolated NVS overlay |
| transport | `PASS` | RSN, M1-M4, peer MIC verification, CCMP RX, DHCP |
| device_response | `PASS` | guest association, DHCP marker, DNS query and TCP/443 |
| data_behavior | `PASS` | correct password connects; wrong password is rejected and gets no DHCP |
| CI | `PASS` | `platform-contracts` and `network-namespace-policy` both succeeded for `08d8a21` |
| visual_or_physical | `NOT RUN` | no physical RF or electrical measurements |

## 验证边界

- 本记录是 `virtual-device validation`，不是 hardware validation；
- 只覆盖 WPA2-PSK pairwise-key 与单播 DHCP delivery；
- WPA3-SAE、WPA2 group-key multicast、真实 RF/PHY、channel/rate、roaming、
  干扰和功耗没有覆盖；
- synthetic OpenAI key 只能证明 guest 发起 DNS/TCP/HTTPS 路径，不能证明真实
  OpenAI 账号、Realtime/WebRTC 或云端业务成功；
- group-key multicast 若要扩展，必须补 guest key installation 和 broadcast
  delivery 的独立验证，不能把当前 pairwise scope 扩大描述。

## 风险与回滚

风险集中在 closed WiFi firmware 的硬件解密 RX 私有布局和 DHCP 的单播交付
假设；两者都由同一公开固件的 guest 回调、DHCP/DNS/TCP 和 pcap 证据约束。
回滚结果提交 `08d8a21bda173ff65dfb5343d0fa8082732eb872` 可恢复
`3f4bf92b96d5854f0804d7f7014c4a9c244da99e` 的 Open-only 行为，不影响物理
设备或生产凭据。

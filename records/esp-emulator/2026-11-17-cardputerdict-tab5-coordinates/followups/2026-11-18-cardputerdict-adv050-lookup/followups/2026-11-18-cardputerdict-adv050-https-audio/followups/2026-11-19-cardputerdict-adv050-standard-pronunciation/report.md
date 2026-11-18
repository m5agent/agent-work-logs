# CardputerDict ADV 0.5.0 原版保存快照发音审核

## 根因

旧版只允许初代 Cardputer 0.6.4 的板卡和原版 SHA256。实际 ADV 的标准保存快照请求返回 HTTP 202，随后在创建 Device Service 会话前进入 E_CARDPUTER_PRONUNCIATION_INCOMPATIBLE，两个预期均保持零会话、零租约。拒绝由审核准入触发。

首个 ADV 候选通过了准入，但真实设备会话未观察到 DHCP 或 SNTP，最终画面在查词框出现了字母 p。下一候选加了词典页确认，仍出现同一结果。对照此前同原版的成功 Device Service 直测及当前板卡输入映射，确认 ADV 的 Fn 与初代 Cardputer 使用不同的虚拟键码。最终候选先等原版词典页出现，再对 ADV 的 Wi-Fi、清空和发音操作使用 compose。初代 Cardputer 的 menu 键路径保留。

## 同原版执行

1. 在无网卡 Linux ARM64 VZ 中加载固定 Device Service 1.99.0 及原生 Xtensa QEMU。Reviewer 基线为 f0101b6，候选为 e7e32f19。原版 ADV BIN、规范化 Flash、SD 夹具和候选软件包摘要见证据。
2. 标准保存快照 dry-run 通过 Device Service 的输入和原生网络隔离执行。测试主机重新用原版内嵌的 CA 核对 TLS；VZ 仅有两种固定用途的 Virtio Socket 转发。测试对照固定同一校时和发音目标。
3. 通过真实 Fn+W 配置测试 Wi-Fi，查询 hello，并通过真实 Fn+P 触发发音。分别核对 DHCP、受控 DNS、SNTP、TLS、缓存和 PCM。在阻断对照中仅拒绝发音目标的实际 TCP 端口，保留校时。
4. 核对停止后的 Reviewer ZIP 和 Device Service ZIP CRC、成员哈希和 PCAP，释放 QEMU、Flash、租约及临时网关资源。

| 原版场景 | 标准重试与终态 | 应用证据 |
| --- | --- | --- |
| ADV 允许 | HTTP 202，done / SIM_VERIFIED | 10,605 字节缓存 MP3，84,992 字节同会话 PCM |
| ADV 拒绝 | HTTP 202，manual_review / SIM_PARTIAL / E_CARDPUTER_PRONUNCIATION_POLICY_DENIED | 发音连接有尝试，保留 SNTP，发音端口无回复、TLS、缓存或 PCM |
| 初代 Cardputer 0.6.4 允许 | HTTP 202，done / SIM_VERIFIED | TLS 和缓存通过，84,992 字节同会话 PCM |

来宾与主机的转发证据核对三笔 SNTP 和两笔 TLS，流量字节数及摘要相符。实际虚拟设备证据绑定两份明确的原版固件。虚拟机、服务和会话资源均已清理，Burner 未提交。常驻审核切换、其他固件、物理声学或射频为 NOT RUN。

[结构化记录](run.json) · [脱敏证据摘要](evidence/adv050-standard-pronunciation.summary.json)

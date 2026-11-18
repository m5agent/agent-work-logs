# CardputerDict 0.6.4 原版的受控 SNTP、HTTPS 和诊断音频

两个新会话使用同一未改 CardputerDict 0.6.4 BIN、同一合成 Flash、同一份自编单词词条 FAT32 卡及同一 Linux Xtensa QEMU 与 ROM。固定的 Device Service 候选在隔离网络命名空间中运行。候选代码保留在本地提交 97ae097ddf1337c327e8bdbeae29642401ed5a74，其中的 OpenAPI 字节和运行时返回值的 SHA-256 一致。两次各接受 18 个按键输入，实际启动、连接来宾 Wi-Fi、进入词条并触发外部发音。原版发布基线的同类网络配置实测 HTTP 400，错误码 allowlist_not_supported，尚未创建来宾会话。[发布基线接口](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service-api.md)

| 来宾观测 | 放行组 | 拒绝组 |
| --- | --- | --- |
| 受控 DNS 和 SNTP | 发音域名得 A 应答，SNTP 请求和对应应答一组 | 发音域名得 A 应答，SNTP 请求和对应应答一组 |
| 发音 TCP 端口 | 一个 SYN、收到 SYN-ACK | 同一连接的两次 SYN，未收到 SYN-ACK |
| TLS | ClientHello 对应原发音域名，出现 ServerHello，双向加密应用记录 | 无 TLS 应用记录 |
| SD 缓存 | 来宾新增一份 10,605 字节 MP3，与前两次放行取证的哈希一致 | 输入和输出卡均无发音缓存 |
| 来宾帧和音频 | 诊断 I2S DMA 采样 60,416 字节，28,426 个非零 s16le 样本 | 返回到词条画面，诊断 DMA 未开启 |

放行组的原始 I2S 采集文件在采样后继续追加到 65,024 字节。采样前缀和停止后的完整留存文件分别记录摘要。逐项核验原始抓包、两份同会话 ZIP 的 CRC 和成员哈希、受控输入、串口、帧及实际 FAT 字节链。两个会话均释放租约，清理 QEMU、命名空间和临时 NAT。资料保留下载内容的哈希及长度。[独立回执](evidence/cardputerdict-https-allow-deny.summary.json)

这组结果验证候选网络路径和诊断 I2S DMA。拒绝对照验证连接及缓存的边界。默认响声、真机、浏览器、常驻审核与 Burner 均为 NOT RUN。完整抓包、ZIP、MP3 和 PCM 只留在本地取证环境。[既有原版数据面记录](https://github.com/m5agent/agent-work-logs/blob/fc8044a17ef6f863c92e47c5a5d338a57a175429/records/esp-emulator/2026-11-18-native-review-data-plane/report.md)

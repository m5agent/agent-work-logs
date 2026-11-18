# CardputerDict 0.6.4 原版在 Device Service 1.89 的默认发音路径

两组分别启动新的隔离 Linux arm64 Device Service 会话。使用同一未改原版 BIN、规范化 Flash、ESP32-S3 ROM 和仅含 hello 词条的 FAT32 夹具。输入夹具无音频。18 个实际按键操作完成联网、查询和发音。两组均使用普通会话接口和默认音频配置。[源码中的执行与边界](https://github.com/m5agent/m5stack-esp-emulator/blob/1319222e0b7439789e35fd177d50b9f0371e3f11/docs/evidence/2026-11-18-cardputerdict-https/README.md)

旧版 1.88 在外部地址策略下实测返回 HTTP 400，错误码 allowlist_not_supported，活动租约仍为零。1.89 的受控 DNS 在明确地址与授权端点范围内，沿用默认拒绝的隔离命名空间。对照组只改发音端口的授权目标，有意保留 DNS 与 SNTP。默认 Cardputer QEMU Wi-Fi speaker 路径把 PCM 持久化到会话，供音频 API 和证据 ZIP 读回。[1.88 接口](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service-api.md) · [1.89 接口](https://github.com/m5agent/m5stack-esp-emulator/blob/1319222e0b7439789e35fd177d50b9f0371e3f11/docs/device-service-api.md)

| 观察 | 放行组 | 拒绝组 |
| --- | --- | --- |
| DNS 和 SNTP | 发音域名取得 A 应答，配对的 SNTP 请求和应答一组 | 发音域名取得 A 应答，配对的 SNTP 请求和应答一组 |
| 来宾抓包 | 57 包，TLS 双向加密应用记录 | 19 包，同一发音连接两次 TCP/443 SYN，无应答或 TLS |
| 实际 FAT32 | 新增 10,605 字节 MP3 | 发音缓存缺失 |
| 来宾声音 | 普通 API、ZIP、停机后 API 分别获得 60,928、61,952、66,560 字节 | 无 PCM，最终画面回到词条 |

从证据 ZIP 独立重算每个成员哈希。普通 API 的 60,928 字节等于 ZIP PCM 的前缀。ZIP PCM 等于停止后最终文件的前缀。样本含 28,426 个非零的 s16le 值，峰值绝对值 7,051。拒绝轮的最终画面和先前词条帧逐字节相同。停止后双侧均释放租约，清理网络命名空间和临时 NAT。[同会话 PCM 和拒绝对照](evidence/same-session-pcm-and-policy.summary.json)

真机音响、浏览器、Cardputer ADV、Reviewer 保存快照和 Burner 仍为 NOT RUN。本记录仅发布音频和抓包摘要。之前的诊断 I2S 对照在独立记录中保留。[前次诊断对照](https://github.com/m5agent/agent-work-logs/blob/3f29e0a112dc60890f1ca4f2a76715a82eb1a810/records/esp-emulator/2026-11-18-native-review-data-plane/followups/2026-11-18-cardputerdict-https-candidate/report.md)

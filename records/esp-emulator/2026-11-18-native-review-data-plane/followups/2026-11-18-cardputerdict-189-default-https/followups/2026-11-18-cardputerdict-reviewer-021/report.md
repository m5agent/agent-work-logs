# CardputerDict 0.6.4 原版保存快照的审核复验

通过 Reviewer 提交 ecc8cfc3aadd5b2ae0289171784d2abac91bf855、Device Service 1.89.0 测试提交 1319222e0b7439789e35fd177d50b9f0371e3f11 和 Linux arm64 原生 QEMU 运行原版固件保存快照。使用同一未改 BIN、Flash、ROM 和 64 MiB FAT32 词条卡。放行与拒绝各接受 18 个按键动作。先前 0.20 的原版保存快照仍保留 E_NETWORK_PARTIAL。直接走 Device Service 的默认音频复验独立归档。[直接 API 原版复验](https://github.com/m5agent/agent-work-logs/blob/3aa0b1b54fd071ed0996738781ac66c0e46de5f6/records/esp-emulator/2026-11-18-native-review-data-plane/followups/2026-11-18-cardputerdict-189-default-https/report.md)

| 试次 | 实际审核终态 | 同会话结果 |
| --- | --- | --- |
| 允许原版发音 | done，发音断言 PASS | 匹配 SNTP、双向 TLS、10,605 字节 MP3、停机后 84,992 字节非零 PCM |
| 发音 TCP/443 超出许可 | manual_review，E_CARDPUTER_PRONUNCIATION_POLICY_DENIED | DNS 和校时通过，TCP 发起后无回应，缓存和 PCM 缺失 |
| 缺少原生隔离 | manual_review，E_CARDPUTER_PRONUNCIATION_ENVIRONMENT | 准入阶段 PARTIAL，零来宾会话、零活动租约 |

核对 Reviewer 持久化的任务终态、保存的证据 ZIP 及独立取得的同会话 ZIP。两个 ZIP 中的 PCAP 和适用的 PCM 均逐字节相同。放行组的 PCM 与停机后 API 相同，峰值 7,051。已创建的两次来宾均释放 Flash、租约和隔离网络，保留历史。[实际任务和同会话取证](evidence/reviewer-021-exact.summary.json)

主分支通过此记录更新当前状态和验收边界。Cardputer ADV、浏览器、物理设备和 Burner 未运行。原音频、抓包与设备标识仅保存在本地取证环境。[主分支发布摘要](https://github.com/m5agent/m5stack-esp-emulator/blob/0e376abc91ddf8252eb565cb1b54204be8e1f089/docs/evidence/2026-11-18-cardputerdict-https/reviewer-saved-snapshot-summary.json)

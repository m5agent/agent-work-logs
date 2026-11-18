# Linux 持久审核卷冷启动回读与重试

同一无虚拟网卡的签名 Apple Virtualization 来宾配置，实际启动两次 Debian ARM64。宿主确认冷启动之间来宾已退出，第二次启动读取同一目录，未恢复快照、复制应用状态或重新录入审核任务。先前的低磁盘中断对照保持原样。

1. 独立的 VirtioFS 目录实测通过 SQLite WAL、读快照、写竞争和 `flock`。使用认证的标准上传入口接收固定 FAT32 词库，原版 CardputerDict 0.6.4 通过保存快照重试启动。设备侧 QEMU、ROM 和固件均按 SHA256 核对。审核停止后确认来宾、临时网络、可变 Flash 和活动租约已释放，保留同会话的 Reviewer ZIP 和 Device Service 证据。两份 ZIP 的 CRC、清单和 PCAP 一致核验。
2. 完成关机后用同一卷冷启动，Linux boot ID 变更。文件系统重新分配了来宾侧 inode，宿主实际目录身份保持一致。标准重试前，Reviewer 回读同一任务和结果，Device Service 回读同一已停止会话、同一 worker 且 generation 增长。已保存 ZIP 字节不变，从 Device Service 再取证得到的 PCAP 与旧 PCAP 逐字节一致，保留 SD 内容哈希不变，活动租约为零。
3. 再次用标准保存快照重试，HTTP 202 后实际创建一个不同的会话，并加载相同原版固件。两轮均在隔离对端与独立来宾 PCAP 观察到 SNTP 和 TCP 443 ClientHello。第二个会话最终正常停止，命名网络、NAT、QEMU、可变 Flash 和租约均释放。最终保留两条 Device Service 会话、一条 Reviewer 任务。宿主再次核对关机、数据库完整性、所有证据与持续状态。

审核的应用层结论仍为 `E_CARDPUTER_PRONUNCIATION_PARTIAL`。受控本地对端未提供可信证书，所以没有完成认证的 TLS、媒体下载或 PCM 播放。冷启持久化结果只适用于本次精确软件版本与隔离卷。未部署常驻 Linux worker，未执行物理设备或 Burner 操作。

复现时使用固定输入与两份精确 API 合约，在专用 VirtioFS 卷保留标准停止后的任务与会话。完成整个来宾关机，再使用同一宿主目录启动。先比较旧任务、活动租约、ZIP 和 PCAP，随后才排队重试并核对新会话的进程、网络及清理。[有界证据](evidence/cold-pair.summary.json)

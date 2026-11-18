# 复现与证据

1. 以 [结构化收据](evidence/cardputerdict-trusted-https.summary.json) 固定发布固件、
   原生 QEMU、VZ runner、内核和源码。用原版内置 CA 做 TLS 1.2 / MP3 预检，
   再核对真实 SNTP originate。固定两个合格的公共地址和协议端口。
2. 用同一份只读 FAT32 一词词库发起两次标准 Reviewer 保存快照重试。隔离 Linux
   实例仅有环回接口与内部试验 veth，外部地址通过两个有凭证的 VSOCK 通道转发。
   原固件保有 TLS 终止和证书校验，内部 Device Service 继续使用受控 DNS、
   nftables 默认拒绝及同会话 PCAP。
3. 阻断轮将审查许可的发音端口改为 444，原版依旧尝试 443。收据为 POLICY_DENIED，
   保留同会话 DNS、SNTP、无 HTTPS 回复，以及无 SD 缓存和 PCM 的对照。
4. 放行轮为 443，确认 done / SIM_VERIFIED，核对同会话 ZIP 的 CRC、成员大小、
   SHA-256、DHCP、DNS、SNTP、双向 TLS、缓存及 PCM。停机后 API 回读同一 PCAP
   和 PCM。两个会话各自停止，Flash、临时 veth、NAT、命名空间和租约均释放，
   外层虚拟机正常退出。

## 首轮失败对照

首轮真实复审在 QMP 就绪前因 gateway handoff descriptor identities are invalid
而被拒绝。原版应用未开始运行，命名网关独立记录了正常清理。另一次代码级对照在
关闭 stdin 时将 guard 分配为 FD 0，出现同样拒绝。首轮未独立采样实际 FD。
成功复验在试验启动器中显式将 stdin 保留为 /dev/null。Device Service 和 Reviewer
源码继续使用原钉版本，早先无可信证书的持久卷 PARTIAL 保留。

此轮证实指定原版、限定外部协议和同一虚拟会话的数字音频。常驻 Linux 路由、
实体扬声器和 RF 仍待其他验收。

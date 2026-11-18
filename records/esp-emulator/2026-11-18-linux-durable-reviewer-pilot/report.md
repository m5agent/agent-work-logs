# Linux 持久审核试验报告

检验原生 Linux Reviewer 和 Device Service 能否共用一个专用持久卷，在完整停机并冷启动后保留审核任务、会话和取证文件。使用经签名验证的 Apple Virtualization 启动器、固定 Debian ARM64 内核与无虚拟网卡配置。输入目录只读，只有独立试验卷可写。两项服务使用固定的公开源代码及 OpenAPI 合约。产品源码无改动。

1. 来宾卷实际识别为 VirtioFS。SQLite 3.46.1 创建 WAL 和 SHM 文件。真实独立进程维持旧读快照，另一个写进程遇到 `SQLITE_BUSY`，随后完整性与 checkpoint 检查通过。专用守护文件的模式、属主、原子改名和跨进程 `flock` 均实测通过。
2. 使用正常服务入口以 HTTP 201 接收 64 MiB FAT32 测试词库镜像。空闲时按字节核对后稀疏化，SHA256 保持一致。以 HTTP 202 提交原版 CardputerDict 0.6.4 `saved_snapshot` 重试。通过活动会话与实际 QEMU 进程核对运行时。对照独立隔离网络端与 4,006 字节来宾 PCAP，观察到 SNTP 请求响应、TCP 443 请求和 ClientHello。测试端没有提供证书，也没有外部网络连接。
3. 宿主报告可用空间跌破 4 GiB。资源门槛结束试验，宿主确认该虚拟机已停止。最后持久状态仍为 Reviewer `running`，Device 会话 `running` 且记录的租约仍活动。原始状态单独保留，常驻服务没有变更。

在满足磁盘余量后复验时，先以相同输入通过标准干跑取得终态与已保存 ZIP，按原会话核对 PCAP 并确认活动租约为零。彻底关闭来宾，再用同一持久卷冷启动，通过服务回读同一任务、会话与 ZIP、PCAP 哈希，然后再走一次标准重试，证明新会话来自同一原版固件。

本次没有验证冷启动恢复、可信 HTTPS 发音、扬声器 PCM、物理设备或 Linux 常驻部署。没有 Burner 提交。[有界证据](evidence/pilot.summary.json)

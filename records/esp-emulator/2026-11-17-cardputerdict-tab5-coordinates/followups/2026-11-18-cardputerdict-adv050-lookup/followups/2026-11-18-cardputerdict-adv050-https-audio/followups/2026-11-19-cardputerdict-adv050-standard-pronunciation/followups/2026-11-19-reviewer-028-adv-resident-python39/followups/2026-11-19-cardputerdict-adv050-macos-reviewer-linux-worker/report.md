# CardputerDict ADV 跨系统保存快照复审报告

## 背景

此前 Reviewer 0.28 已验证同源 Linux 复审与 macOS Python 3.9 启动。本次单独运行 macOS 原生 Reviewer，经受限的 HTTP/VSOCK 适配器连接一台无 NIC 的 Linux VM，覆盖两部分之间的整条复审路径。虚拟设备使用同一份原版 `CardputerDict ADV 0.5.0`，SHA-256 `21b7a88e7e58f18674184a58193d30f2722ddd690b4803d9b403b63ec0796d14`。

## 执行

1. 从记录中的完整 Git 版本分别打包 Reviewer 0.28.0 和 Device Service 1.99.1。用 macOS `/usr/bin/python3` 3.9.6 启动 Reviewer。Linux 通过 Apple Virtualization.framework 运行。VM 无虚拟网卡，启动时仅见回环接口，无 IPv4 或 IPv6 默认路由，Device Service 绑定回环。会话使用专用隔离命名空间。在 guest 和 macOS 侧分别检查 Device Service OpenAPI 哈希。
2. 启用仅支持宿主 CID 的 VSOCK 接收端和仅回环的宿主监听。上传授权限定到原版 BIN 的精确大小与 SHA-256，且固定板型、固件、SD、网络策略和一个会话。用缺失认证、错误认证、越界路由、他会话、错误方法和错误固件请求检查边界。
3. 将同一原版准备为两份保存快照，调用标准 `POST /api/reviews/{id}/retry`，设置 `sourceMode=saved_snapshot`、同一 SD 工件以及 `validation.cardputerdict_pronunciation.expect` 的 `playback` 或 `blocked`。使用源码中的板型专用输入路径，固件在原会话完成查询与发音。先运行允许策略，再运行禁止策略。两轮确认 Device Service 宣告 `review-v1` 恢复能力，Linux worker 身份与代次一致；复审完成后没有未清理的会话创建意图。
4. 通过正常 Reviewer 终态与 Device Service 停止后证据端点分别回读 ZIP。验 ZIP 内清单及每个文件的字节数和哈希，比较初次留证和停止后回读中的同会话 PCAP 和 PCM。对比宿主与 Linux 对等侧的 SNTP/TLS 原始字节指纹。
5. 检查两个会话的租约、可写 Flash、QEMU 和网关均已释放。等待 Linux guest 正常退出和 VM 停止确认、关闭宿主监听，检查 macOS Reviewer、guest 和适配器进程已退出。

## 验证结果

| 层级 | 状态 | 观测 |
| --- | --- | --- |
| HTTP/VSOCK 传输 | `PASS` | 两次 HTTP 401，四次 HTTP 403，可授权请求往返。两次 SNTP 和一次 TLS 在宿主与 guest 两侧匹配。 |
| 允许策略 | `PASS` | HTTP 202，`done / SIM_VERIFIED`，`authenticated_download_and_i2s`。DNS、SNTP 和 TLS 通过。SD MP3 为 10,605 字节，I²S PCM 为 84,992 字节，非零 16 位峰值 7,051。 |
| 禁止策略 | `PASS` | HTTP 202，`manual_review / SIM_PARTIAL / E_CARDPUTER_PRONUNCIATION_POLICY_DENIED`，拒绝原因 `tcp_443_outside_allowlist`。DNS、SNTP 和 HTTPS 尝试可见，SD 缓存与 PCM 均无产出。 |
| 证据回读与清理 | `PASS` | 四个 ZIP 完整可读，两轮各自 PCAP 与可用 PCM 一致。两轮活跃租约均为 0，会话 Flash、网关与进程退出。guest 状态 0，VM 停止确认，桥接关闭。 |
| 物理设备及生产流量 | `NOT RUN` | 本次测试使用隔离虚拟设备，覆盖协议、SD 和 I²S 数字数据路径。物理声音、RF、硬件时序、线上路由和 Burner 提交均超出执行范围。 |

首轮夹具在第一笔鉴权请求前触发 Python 模块名覆盖，未发送复审请求。首轮 VM 已停止并关闭监听。修正私有夹具的 HTTP 导入后，第二轮从新的隔离状态完成完整验收。两个尝试原始回执的大小、SHA-256、有效试验源码、运行时和 ZIP 哈希均见 [脱敏证据](evidence/macos-linux-vsock-adv.summary.json)。没有产品代码变更需要回滚。

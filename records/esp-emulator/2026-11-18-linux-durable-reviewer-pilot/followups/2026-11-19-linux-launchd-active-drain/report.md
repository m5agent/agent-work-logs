# Linux 受管 worker 活跃审核排空验证

初次 A3 中，Linux 来宾已准备好，但宿主桥在审核准入前因未捕获的 `socket.timeout` 退出。实际系统 Python 3.9.6 下，该异常与内建 `TimeoutError` 的类型关系不满足旧处理分支。此次没有创建审核租约，失败状态和隔离标记保留。随后仅对已确认零租约的自有来宾执行清理，收到了真实关停回调；隔离卷的正常重启仍被拒绝。

修正桥的接受连接与转发等待分支，使其捕获实际 `socket.timeout`。在系统 Python 3.9.6 中，旧桥的两个真实 TCP／套接字测试均出现预期失败，新桥两个测试通过，另有六项控制器检查通过。这些回归没有启动新的虚拟来宾。 [现有证据](evidence/linux-launchd-active-drain.summary.json)

A4 中，macOS Reviewer 0.29.2 通过专用认证桥，向 Linux Device Service 1.99.3 提交同一 Core2 2048 原版。实际棋盘画面出现且只有一个绑定租约后，向自有 LaunchAgent 发送了 SIGTERM。worker 关闭新会话准入，原审核和证据传输持续可达。

| 环节 | 结果 | 实际证据 |
| --- | --- | --- |
| 关闭准入 | PASS | 信号时一个活跃租约；新的创建请求得到 503 |
| 继续审核 | PASS | 同一个运行中来宾仍返回 HTTP 200，并提供七个清单载荷的真实 ZIP |
| 原版 2048 | SIM_VERIFIED | 四方向各两次合法移动；独立重新解析成对画面和新方块，原 BIN 与归一化 Flash 精确绑定 |
| 第一代正常退出 | PASS | Device Service 租约归零并退出，真实来宾正常停止回调与该代凭证匹配，LaunchAgent 退出码为零 |
| 后继代次读取 | PASS | 原 worker 身份相同且启动身份改变，同一端点与持续运行的 Reviewer 数据库重读成功，无重复来宾 |
| 保留数据 | PASS | 关闭前与后继代次的同一个停止会话，七个归档载荷逐字节相同 |

独立重开四份 ZIP，逐项核对 30 个清单载荷的 CRC、长度与 SHA-256。其中排空期 ZIP 和 Reviewer 终态 ZIP 的来宾状态为 running，两份独立 Device ZIP 为 stopped。后两份归档的七个载荷相同，清单会话身份固定，恢复后的元数据仅改变了事件计数和恢复标记。一次辅助 HTTP 监视在对端关闭时因断开退出，最终停止状态另由真实进程和关停回执独立核对。 [有界复核证据](evidence/linux-launchd-active-drain.summary.json)

两代均完成 Device Service 正常退出和来宾正常停止回调，试验角色已卸载，端点撤下、持久卷锁释放，保留两条停止会话。辅助 HTTP 监视的断开没有被作为关停凭证。

第二代另跑了同一原版 CardputerDict 0.5.0。启动与 60 秒观察通过，发音结果为 `SIM_PARTIAL` / `E_CARDPUTER_PRONUNCIATION_PARTIAL`。独立 PCAP 重算确认一次 DHCP DORA、一次 NTP 域名的 DNS 请求与回复，以及一条没有收到回复的 SNTP 请求；没有发音域名 DNS、TLS 流量、缓存或 PCM。宿主转发助手在系统 Python 3.9 导入时触发 `dataclass(slots=True)` 不兼容错误，尚未进行转发。外层收集器另遇到缺少 `source_artifacts` 字段的 KeyError，原报告和类型化 ZIP 中的部分结果完整保留。

此后只把转发助手的宿主解释器固定到散列核对过的 Python 3.13.15，完整无网络导入预检通过。试验角色保持卸载。可用存储低于既有启动预留要求，因此修正后的同原版 ADV 路径为 `NOT RUN`。这次解释器预检不构成发音问题已解决的证据。

本次没有生产路由切换、登录重启或操作系统重启。物理硬件、浏览器 WASM 与 Burner 提交均为 `NOT RUN`。原始配置、主机日志、端点和会话标识留在私有证据存储。此前受管 worker 的成功和失败结果继续保留。 [原验证记录](https://github.com/m5agent/agent-work-logs/blob/a325a930fb3c8a2afcd6bb084384f38383de3be6/records/esp-emulator/2026-11-18-linux-durable-reviewer-pilot/followups/2026-11-19-linux-managed-worker-two-originals/report.md)

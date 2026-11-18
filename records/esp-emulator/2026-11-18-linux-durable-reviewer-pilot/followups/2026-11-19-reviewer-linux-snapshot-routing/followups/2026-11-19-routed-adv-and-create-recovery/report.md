# Reviewer 0.30 原版 ADV 路由与 Core2 创建响应丢失恢复

两项测试使用同一个托管 Linux 代次、固定的 Device Service 1.99.3 与 Reviewer 0.30.0 源码。Reviewer 提交为 `b9426a2d8a88338d95346ed9b93b0eaf0893cb9a`，Device Service 为 `2a7f979c0c7e67420d8b790a3cfdb692702abf05`。测试使用独立状态，并为两款应用分别固定原版固件、启动依据及初始 Flash，源码和运行时摘要列在证据中。 [先前路由记录](https://github.com/m5agent/agent-work-logs/blob/34a39d9d3bdde715f43eb2277765842ee4217c9f/records/esp-emulator/2026-11-18-linux-durable-reviewer-pilot/followups/2026-11-19-reviewer-linux-snapshot-routing/report.md)

| 验证路径 | 结果 | 直接证据 |
| --- | --- | --- |
| CardputerDict ADV 0.5.0 普通保存快照复审 | SIM_VERIFIED | 实际 Linux 会话与创建意图、选路事件一致，Darwin 未创建会话；18 步真实输入、60.045 秒的 13 帧观察通过 |
| ADV 网络与发音 | PASS | SNTP 请求与回复各 48 字节，双向 TLS 数据与宿主、Linux 日志逐项相同；缓存 10,605 字节 MP3，三份归档及 API 回执匹配同一 84,992 字节 PCM |
| ADV 空闲重开 | PASS | 同一数据库的一条任务、21 条事件和证据精确保留；关闭新准入后 Linux 就绪为 503，Darwin 主就绪仍为 200 |
| Core2 创建响应丢失与 Reviewer 重启 | PASS（会话处置） | 后端真实创建返回 202，成功响应交付为零字节；只终止自有 Reviewer 进程，Linux 来宾继续运行；恢复期间关闭新准入，找到并停止同一原版会话 |
| 原中断任务 | service_error | 保留 `SIM_PARTIAL / E_SERVICE_RESTART`，未发起新尝试；故障控制器的主后端请求计数为零 |
| 本代最终关闭 | PASS | 匹配的 Device Service 退出和来宾正常停止回调，六条会话历史均为 stopped，租约归零，端点撤下、卷锁释放、临时角色卸载 |

Core2 的普通审核请求先被接受为 202。受控代理随后收到后端真实创建的 202 响应，并在绑定会话前将其截住，未向 Reviewer 送出响应字节。持久创建意图仍未绑定时，对自有 Reviewer 发送 SIGKILL。重新启动同一数据库并关闭新 Linux 准入后，产品执行一次创建意图协调、读取并停止原会话。数据库中的恢复事件为 complete/released，创建意图归零。前后归档的同一个 2048 棋盘和串口逐字节相同，原有任务继续保留中断错误。此轮没有正常重试或新建替代来宾。

独立重开 ADV 的三份 ZIP，共核对 35 个清单载荷的 CRC、长度和 SHA-256，并重组实际 PCAP、核对两边转发日志、重新读取 SD 缓存和 PCM。Core2 恢复前后的 ZIP 分别含八个与七个载荷，共 15 个逐项验证；恢复前 Flash 中 `0x10000` 的 505,760 个应用字节与原版精确相同，恢复后归档已没有工作 Flash 载荷。两项证据绑定同一托管代次，但使用各自独立会话和审核数据库。 [完整有界证据](evidence/routed-adv-and-create-recovery.summary.json)

验证覆盖 Reviewer 进程终止后的持久意图协调，以及本代之后的正常关停。虚拟机崩溃、持久卷崩溃、操作系统重启、物理硬件、浏览器 WASM、生产变更和 Burner 提交均为 `NOT RUN`。原始 BIN、Flash、媒体、网络捕获、数据库、主机配置和唯一标识留在私有证据存储。

# Reviewer 0.29 原版发音复审冷恢复报告

## 背景

前一轮使用 Reviewer 0.28 完成了 macOS Reviewer、认证 VSOCK 与无网卡 Linux Device Service 跨系统同卷冷恢复。本轮固定 Reviewer 0.29.0 `69386c6`，在相同虚拟化基座和 Device Service 1.99.1 `c9ec0f27` 上复验。文档主分支 `8e4909f9` 中的 Device Service 源码和 OpenAPI 与运行包逐字节一致。新审核的 Flash 静态诊断改动不改变本次复用的恢复与 ADV 发音模块。

## 执行

1. 从精确 Git 版本给 macOS 系统 Python 3.9.6 准备审核程序和 API 契约。Linux 无网卡，使用独占的 VirtioFS 状态卷和固定认证回环 VSOCK 地址。验证缺少或错误认证的 HTTP 401 和越界请求的 HTTP 403。
2. 以相同原版 CardputerDict ADV 0.5.0（SHA-256 `21b7a88e7e58f18674184a58193d30f2722ddd690b4803d9b403b63ec0796d14`）、同一 SD 种子和 `playback` 参数发起标准 `POST /api/reviews/{id}/retry`，使用 `sourceMode=saved_snapshot`。HTTP 202 后确认活动 QEMU、已提交网关、磁盘租约、可写 Flash、绑定的 Reviewer 创建意图和实际 SNTP，然后停止 macOS Reviewer。宿主撤销旧监听与转发，取得旧 VM 停止确认。
3. 后继 Linux 挂载原卷。使用原地址、认证配置和 SQLite 启动同一 macOS Reviewer，原审核记为 `E_SERVICE_RESTART`。无控制器凭证时，标准重试返回 HTTP 409 和 `device_service_recovery_unconfirmed`。保留一条旧租约和工作 Flash，抓包与原记录匹配，原证据 ZIP 可回读。
4. 由宿主根据旧 VM 已终止、同一独占卷、后继启动身份与精确网关哈希提供卷外只读凭证。同一后继 Linux 启动再次启动 Device Service，原审核会话终结，租约、工作 Flash 和 Reviewer 创建意图释放。再次读取旧证据 ZIP，核对 PCAP 与每个网关、隔离记录的 SHA-256。
5. 从相同保存快照发起标准重试，确认 HTTP 202、新会话和 `done / SIM_VERIFIED`。核对可信 TLS 下载、10,605 字节 MP3、84,992 字节 PCM，以及 Reviewer 和 Device Service ZIP 中的逐字节载荷。结束后独立离线重读四份 ZIP 和控制器回执，不追加虚拟机启动。

## 验收与限制

| 验收项 | 结果 | 依据 |
| --- | --- | --- |
| 无凭证保护 | `PASS` | HTTP 409，旧租约=1，工作 Flash 与原始证据仍可回读 |
| 精确凭证恢复 | `PASS` | 旧网关/隔离日志以及 PCAP 字节一致，旧租约/Flash/Reviewer 创建意图均归零 |
| 同一原版重试 | `PASS` | `done / SIM_VERIFIED`，SD MP3 与 I²S PCM 实际读回，成对 ZIP 载荷一致 |
| 运行清理 | `PASS` | 两台 VM 停止、两个桥接和辅助转发退出，无活动租约 |
| 常驻 Linux 路由、宿主断电、物理设备 | `NOT RUN` | 本次使用独立状态、回环地址与宿主停机确认，只测虚拟设备数字路径 |

原 0.28 记录保留。0.29 首次改版试验和独立回读均通过。没有生产流量切换或 Burner 提交。完整版本、字节数、回执和数据哈希见 [脱敏证据](evidence/reviewer-029-cross-host-cold.summary.json)。

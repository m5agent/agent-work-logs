# 原版发音复审的活动租约冷恢复报告

## 背景

前一轮覆盖 macOS Reviewer 通过 VSOCK 调用无网卡 Linux Device Service，并在 CardputerDict ADV 0.5.0 原版上执行放行与拒绝两种标准复审。另一轮覆盖 Linux 内部 Reviewer 在原卷冷启动时的可信回收。本轮把跨系统 API 调用和活动原卷冷恢复放在同一次隔离演练中。Device Service 运行 `c9ec0f27`，文档提交 `71d22d91` 的 Device Service 字节及 OpenAPI 与之相同。macOS Reviewer 固定 `37d7675`，使用系统 Python 3.9.6。

## 可复现实验

1. 使用同一原版 `CardputerDict ADV 0.5.0`，BIN SHA-256 `21b7a88e7e58f18674184a58193d30f2722ddd690b4803d9b403b63ec0796d14`，在专用 macOS 审核数据库生成保存快照。Device Service 绑定独占、持久的 VirtioFS 状态卷。宿主配置一个固定回环地址，VSOCK 仅接纳宿主端，认证错误返回 401，越出限定的路由、会话或工件返回 403。来宾没有虚拟网卡。
2. 调用标准 `POST /api/reviews/{id}/retry`，指定 `sourceMode=saved_snapshot`、固定 SD 工件及发音 `playback`。确认 HTTP 202、Reviewer 已绑定会话创建意图、同一原版 QEMU 活动、网关交接已提交、可写 Flash 已分配。收到 SNTP 并保存非空 PCAP 后停止该 macOS Reviewer。宿主撤销旧桥接和独立协议转发，收到旧 VM 停止确认，记录卷、原始启动和网关日志哈希。
3. 后继来宾挂载原独占卷，Linux 启动身份改变、worker 身份保持一致且代次前进。使用同一认证后端地址和 SQLite 重启 macOS Reviewer，原审核按 `E_SERVICE_RESTART` 停止。无宿主凭证时重试获得 HTTP 409 和 `device_service_recovery_unconfirmed`。原会话保持 `stopping`；一条旧租约、原 Flash 和原 PCAP 继续保留。原 evidence ZIP 可从正常 Device Service API 回读。
4. 宿主结合旧 VM 停止确认和后继启动身份，在状态卷之外的只读共享目录提供精确网关凭证。保持后继 Linux 启动不变，重新启动 Device Service 和 macOS Reviewer。观察 `namespace_gateway_cold_recovered`，原会话终结、旧租约与可写 Flash 释放、旧 Reviewer 创建意图结清。前后两份旧证据 ZIP 与保存的 PCAP 逐字节匹配，原网关和隔离日志 SHA-256 保持一致。
5. 对同一保存快照发起标准重试，取得 HTTP 202、新会话和 `SIM_VERIFIED`。用正常 API 和留档 ZIP 核对数据并关闭所有试验进程。两轮各有一笔经过实际转发校验的 SNTP，正向重试另有一笔匹配的 TLS。

## 结果与边界

| 验收项 | 结果 | 依据 |
| --- | --- | --- |
| 无凭证保护 | `PASS` | 重试 HTTP 409、旧租约为 1、旧 Flash 和旧 PCAP 保留 |
| 可信凭证恢复 | `PASS` | 同一后继 Linux 启动，旧租约与 Flash 回收，状态和原证据一致，创建意图为 0 |
| 同一原版重试 | `PASS` | `done / SIM_VERIFIED`，10,605 字节可信 HTTPS MP3 写入 SD，84,992 字节 I²S PCM，四份 ZIP 完整并逐项比对 |
| 清理 | `PASS` | 两台 VM 先后确认停止，关闭桥接与协议转发，租约为 0 |
| 常驻生产路由、Reviewer 0.29、主机断电和真机 | `NOT RUN` | 演练使用独立基础设施，停机有当前宿主控制器确认，设备输出为数字数据证据 |

首两次启动分别发现私有夹具脚本权限和拓扑标记缺失，均在创建任何原版会话前停止。已保留两个回执。第三次完成真实运行、复审与清理，最外层采集器随后在比较带结构的协议长度数据时失败。另一个读取器在离线对同一批闭合回执逐项检查后得到 PASS，无需重新启动系统。原始数据的大小、SHA-256 和复验项目见 [脱敏证据](evidence/cross-host-active-cold.summary.json)。本次范围没有需要回滚的生产变更，Burner 提交 `NOT RUN`。

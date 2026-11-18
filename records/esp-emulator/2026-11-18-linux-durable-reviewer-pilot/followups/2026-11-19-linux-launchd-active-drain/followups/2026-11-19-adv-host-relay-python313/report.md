# CardputerDict ADV 原版发音的宿主转发修正

上一轮受管 Linux 角色中的 CardputerDict ADV 0.5.0 已正常启动，但宿主转发助手在 Python 3.9 导入 `dataclass(slots=True)` 时失败。实际 PCAP 中有校时 DNS 回复及一条 SNTP 请求，没有 SNTP 回复或后续发音下载，结果为 `SIM_PARTIAL`。原报告、类型化 ZIP 和外层收集器的字段错误均已保留。 [固定历史记录](https://github.com/m5agent/agent-work-logs/blob/6db33a77280f0039824f300e4f7a6a2da6c79797/records/esp-emulator/2026-11-18-linux-durable-reviewer-pilot/followups/2026-11-19-linux-launchd-active-drain/report.md)

这次沿用同一持久 worker 的后续 LaunchAgent 代次，固定宿主转发解释器为经过字节核对的 Python 3.13.15。macOS Reviewer 继续使用 Python 3.9.6 和发布提交 `88ca2e3c325565c2cc0f1099c9d98260fd78386a`，合约为 `0.29.2`。Linux Device Service 源码为 `2a7f979c0c7e67420d8b790a3cfdb692702abf05`，合约为 `1.99.3`。原版 BIN、初始归一化 Flash 与 64 MiB SD 种子的摘要保持相同。

| 验证项 | 结果 | 实测 |
| --- | --- | --- |
| 标准保存快照审核 | SIM_VERIFIED | 同一原版完成 18 步真实键盘输入，报告终态 done，无错误码 |
| 校时 | PASS | 同会话 SNTP 请求与回复各 48 字节，原始 PCAP、宿主及 Linux 转发记录的摘要全部相同 |
| TLS 发音下载 | PASS | 原始 TCP 流重组为客户端 561 字节、服务端 16,179 字节；双方转发记录逐项匹配，并确认双向 TLS 数据交换 |
| SD 缓存 | PASS | 独立读取保留的 SD 镜像，缓存 MP3 长度 10,605 字节，摘要与审核回执相同 |
| 虚拟音频 | PASS | 三份原始归档中的 84,992 字节 speaker PCM 完全相同，摘要也与当时 API 回执一致 |
| 清理 | PASS | 新增一个会话，完成后停止并释放可变 Flash，租约归零，自有 Reviewer 退出 |

独立重开完整 Reviewer ZIP、发音专用 ZIP 和停止后的 Device ZIP，分别核对 16、8、11 个清单载荷的 CRC、长度与 SHA-256。完整 Reviewer ZIP 的来宾状态为 running，另两份为 stopped，三份均绑定同一会话。独立比对归一化 Flash 的全部应用分区与原版内容，再从 PCAP 重组 SNTP、TCP 载荷，核对宿主和 Linux 两边的原始日志后缀。原 SD 镜像也重新解析并验证了缓存文件。 [完整有界证据](evidence/adv-relay-python313.summary.json)

验证范围为这份原版在隔离受管 Linux 角色中的校时、允许目标的 TLS 下载、缓存与 I2S PCM 路径。物理 RF、真实扬声器声学、浏览器 WASM、生产路由切换及 Burner 提交均为 `NOT RUN`。原始 BIN、SD 镜像、PCM、ZIP、主机日志和唯一会话标识保留在私有证据存储。

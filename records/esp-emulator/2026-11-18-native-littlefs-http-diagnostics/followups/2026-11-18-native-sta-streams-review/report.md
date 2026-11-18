# Cardputer 本地 HTTP POST 与 TCP 保存快照审核

在可创建网络命名空间的 Linux 隔离 worker 上，使用同一未替换的 8 MiB ESP32-S3 专用夹具复跑 Cardputer 与 Cardputer ADV。功能源码固定为 Device Service `178d7a41c84ecf9f3b99fe6e742476b4c3f22286` 和 Reviewer `8a6640f7ce7698116c71174c8dad35d71bb8dc86`，新合约分别为 `1.86.0`、`0.20.0`。原有的 GET、DNS A/NXDOMAIN 与二进制 UDP 继续运行。HTTP POST 使用固定 Host、请求路径和二进制正文，TCP 使用两字节大端长度前缀和二进制正文。

| 独立保存快照 | HTTP POST | TCP | 应用层 |
| --- | --- | --- | --- |
| Cardputer 正向 | PASS | PASS | PASS |
| Cardputer ADV 正向 | PASS | PASS | PASS |
| ADV 仅修改 POST 回复末字节 | FAIL | PASS | FAIL |
| Cardputer 仅修改 TCP 回复末字节 | PASS | FAIL | FAIL |
| ADV 缺少命名空间准入能力 | PARTIAL | PARTIAL | PARTIAL，分配租约前返回 503 |
| Reviewer 0.20 和原 GET/DNS/UDP 夹具 | 不适用 | 不适用 | PASS |
| Reviewer 0.19 和原 GET/DNS/UDP 夹具 | 不适用 | 不适用 | PASS |

启用了新夹具且准入成功的四条会话均捕获一次 DHCP DORA、三条双向 TCP 载荷流、三条双向 UDP 载荷流。错误回复同样完整发送，由来宾逐字节检查后给出该项失败状态。两个 Reviewer 版本使用无新增选项的同一旧固件分别验证了 GET、DNS 和 UDP。没有网络准入能力的对照没有创建联网来宾。

Chromium 通过隔离的 Reviewer HTTP 读取已有审核。ADV 正向、ADV 错误 POST 和 Cardputer 错误 TCP 的两列徽标分别显示通过／通过、未通过／通过和通过／未通过。首次测试因导入副本仍指向原证据目录而没有加载报告。修正隔离副本的路径后，逐例核对 HTTP 返回与留存报告相同，并核对服务返回的 HTML 摘要。 [详情页三例回读](evidence/reviewer-browser.summary.json)

功能提交的本地平台套件执行 2,430 项，跳过 10 项，零失败。Reviewer 263 项及包含留存证据的文档版本 51 项检查通过。固定文档提交的 GitHub CI 通过平台合约与网络命名空间策略两项作业。 [固定源码证据](https://github.com/m5agent/m5stack-esp-emulator/blob/7781a8f1a2af4e084dc6e90d1de5d6ac19d553a5/tests/network/native_sta_peers/local-streams-saved-review-summary.json) · [CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44211652376)

## 核验范围

Linux 容器未发布宿主端口，外层容器网络禁用。已准入的会话在自己的命名空间运行，证据记录无外部路由、默认拒绝规则、固定端点准入和所有对端清理。复跑保留停止后的同会话 ZIP 和独立回读 ZIP，核对运行时、板型、固件、最终 PCAP 和 UART。独立复算了四会话的八条应用流，按各自的 TCP 握手和顺序重组整条请求、回复，验证二进制长度与摘要，对每个端点核对恰好一次对端回执和串口终态。

整单继续为 `SIM_PARTIAL` / `E_NO_FRAME`，因为这些固定夹具只通过串口报告，不提供应用画面。验证范围限于隔离的本地 IPv4 数据面、两份夹具和两个板型。物理 Wi-Fi、任意互联网端点、浏览器 WASM 和 Burner 提交未执行。 [七次保存快照的有界摘要](evidence/linux-sta-streams.summary.json)

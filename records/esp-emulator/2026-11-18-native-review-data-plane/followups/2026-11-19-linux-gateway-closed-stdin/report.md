# Linux 审核网关关闭 stdin 的 A/B 回归

## 故障和修复

关闭 FD 0 后，外层网关实际打开的启动 guard 文件占用了 FD 0。基线把该描述符原样传给内层。内层对交接描述符执行身份校验并拒绝该值，审核 API 随后返回启动错误。同一固件和原生运行包用于修复前后的对照。

修复使用 Linux 的 `F_DUPFD_CLOEXEC` 将需要交接的低位描述符复制到 FD 3 或更高位置。临时副本在启动范围退出时关闭。内层现有的身份校验、启动许可、出口策略和网关清理继续执行。源码变更位于 `platform/tools/network_sandbox.py`，对应回归位于 `platform/tests/test_network_sandbox.py`。

## 执行

1. 在无网卡的 Linux ARM64 VZ 来宾中分别加载基线 `1939e39885d3cffe74f01576182bfa28c6148dd2` 和修复 `4216d548477d0b7a52b72f5e07dd07d98d7e8d63` 的 Device Service 源码。复用同一原生 `qemu-wifi` 运行包、Reviewer `f0101b6bb0926a69ef2f8477ae81e991338391f5`、原版 CardputerDict 0.6.4 BIN 和 SD 夹具。版本和产物的 SHA256 见结构化记录和证据摘要。
2. 在外层启动入口关闭 stdin，用 `fstat(0)` 的 `EBADF` 确认。记录真实 guard 创建结果和内层接收到的描述符值。通过标准 Reviewer 重试接口提交 `sourceMode=saved_snapshot`，将 `cardputerdict_pronunciation.expect` 设为 `blocked`，基线与修复分别得到终态。修复版再以 `playback` 运行另一台独立的同型号 QEMU 会话。三个重试请求均返回 HTTP 202。
3. Reviewer 经 Device Service 的键盘输入接口让原版连接测试 Wi-Fi，查询 `hello` 并触发发音。出口对照固定同一处 SNTP 和同一处 TLS 服务，预检使用固件配套 CA 和 TLS 1.2。允许场景只开放所需出口，拒绝场景保留 SNTP 并拦截发音连接。VZ 与测试主机间使用限用途的 Virtio Socket 转发。
4. 对照审核终态、保存的 PCAP、SD 缓存和数字 PCM。在停机后通过 Device Service 读回 ZIP，校验 ZIP CRC、文件清单及摘要。在失败基线复核失败证据和回收结果，在两个候选会话复核虚拟 Flash、租约、QEMU 进程和临时网关资源。

## 观察

| 试跑 | 实测外层 guard / 内层 guard / permit | Reviewer 终态 | 应用行为 |
| --- | --- | --- | --- |
| 基线 | 0 / 0 / 3 | `service_error` · `SIM_PARTIAL` · `E_SIM_STARTUP_FAILED` | 内层拒绝交接，活动 QEMU 会话为 0，实际出口连接为 0 |
| 修复，拒绝场景 | 0 / 5 / 3 | `manual_review` · `SIM_PARTIAL` · `E_CARDPUTER_PRONUNCIATION_POLICY_DENIED` | DNS、SNTP 匹配，HTTPS 有尝试、无回复，MP3 缓存与 PCM 缺席 |
| 修复，允许场景 | 0 / 5 / 3 | `done` · `SIM_VERIFIED` | DNS、SNTP、TLS 交换通过，缓存匹配固件 CA 预检取得的 MP3，PCM 为 84,992 字节 |

候选两次会话各完成一次直接 SNTP 事务，允许场景完成一次直接 TLS 事务，来宾与主机的转发字节数和摘要一致。两种无效授权探针各被拒绝，均产生零上游连接。候选的审核 ZIP 和 API ZIP 分别校验成功，每次的两份 ZIP 内 PCAP 逐字节一致。

基线返回标准失败 ZIP，并回收网关命名空间、临时接口、NAT 和可写 Flash。修复版两个会话都进入 `stopped`，QEMU 已回收，活动租约为 0，可写 Flash 已释放，相关网关和内核资源已清理。两台 VZ 来宾正常退出。证据摘要列出原始终端回执、单场回执、ZIP 和 PCAP 的 SHA256，省略端点和任务、会话标识。

## 验收边界和回退

虚拟设备验证覆盖原版 CardputerDict 发音和指定 Linux 启动路径。真机声学、RF、通用来宾联网、常驻 worker 接入和部署为 NOT RUN。Burner 未提交。若需撤销修复，可独立回退 `4216d548477d0b7a52b72f5e07dd07d98d7e8d63` 后重跑同一组对照。

[精确版本和检查结果](run.json) · [脱敏证据摘要](evidence/linux-gateway-closed-stdin.summary.json) · [ESP Emulator 源码仓库](https://github.com/m5agent/m5stack-esp-emulator)

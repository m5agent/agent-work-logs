# 执行报告

## 目标与前置条件

在完成无网卡 Linux Worker 只读验证之后，使用标准 Reviewer 保存快照 API 覆盖写入、
查询、取证与会话清理。使用同一份 505,760 字节原版应用和匹配启动上下文，
不改原版字节。固定 Device Service 1.99.0、Reviewer OpenAPI 0.27.0、Linux QEMU 和
ROM 资源集合。Linux VM 与内部 Core2 QEMU 都关闭虚拟网卡。
[前一轮只读记录](https://github.com/m5agent/agent-work-logs/blob/aaaf7bcbe4d1ac40c57646524be3b9f93f77fb5f/records/esp-emulator/2026-11-18-linux-durable-reviewer-pilot/followups/2026-11-18-linux-vz-worker-vsock/README.md)

## 运行与结果

1. 创建新状态目录和独立 Reviewer。签名的 VZ 进程只监听宿主环回，并通过 Virtio
   VSOCK 连接来宾桥接，来宾桥接只接受宿主来源且仅转发到该试验的 Device Service。
2. 验证缺少或错误凭证的 HTTP 401，以及正常凭证但访问会话范围之外的 HTTP 403。
   检查实际 Linux Worker 的零租约、实际 OpenAPI 内容和 Reviewer 就绪。
3. 用 `sourceMode=saved_snapshot` 请求原版任务标准重试。HTTP 202 接受一条任务。
   通过正式 API 上传应用与引导段、组合 Flash、静态分析、创建真实 QEMU 会话。
   只允许固定固件、板型、QEMU 和本轮持有的一个会话。
4. Reviewer 从同一来宾取帧并执行触控，记录左、右、上、下四向棋盘变化，
   终态为 `done / SIM_VERIFIED`。证据 ZIP 为 328555 字节，
   校验 CRC、清单成员大小和 SHA-256，并检查原版和组装 Flash 绑定。
5. 确认执行了标准停止与创建意图对账，已停止会话仍可读。两端核对零租约，
   无需补救清理。临时 Flash、QEMU、Device Service、Reviewer、监听和虚拟机均已释放或退出。

前两轮干跑在桥接的会话准入处停止，已通过的固件上传与静态分析保留。这是试验桥接
对默认 QEMU 和正式创建所有者格式校验过严，之后依据正常 Reviewer 请求调整。
另一次清理观测读到已消失的进程链接。未用这些轮次推定应用失败。

## 证据范围

原始状态、日志与 ZIP 仍保存在私有试验目录，记录不含会话或设备唯一标识、
凭证、内部端点或原版二进制。持久化及重启边界沿用各自证据，当前记录仅覆盖
此轮标准干跑。常驻流量迁移、真机触摸以及公网播放仍未验证，Burner 未提交。
[Device Service 源码许可证](https://github.com/m5agent/m5stack-esp-emulator/blob/7babbf9692c403cfc7052d8b9008d915b19a4418/LICENSE)。
记录不重新分发原版应用、启动上下文、ROM、运行时或独立试验程序。
[执行摘要](evidence/core2-vsock-reviewer.summary.json)

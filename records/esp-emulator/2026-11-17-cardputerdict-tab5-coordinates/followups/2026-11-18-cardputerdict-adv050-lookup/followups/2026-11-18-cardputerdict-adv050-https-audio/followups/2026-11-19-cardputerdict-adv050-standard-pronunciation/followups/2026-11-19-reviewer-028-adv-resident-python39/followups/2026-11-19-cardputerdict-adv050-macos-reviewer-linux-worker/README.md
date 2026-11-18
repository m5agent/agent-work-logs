# CardputerDict ADV 0.5.0 跨系统固件复审

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PASS`（虚拟设备验证）
- 工作类型 `report`，承接 [Reviewer 0.28 macOS Python 3.9 验证](../../README.md)
- 源码 `esp-emulator @ c9ec0f274579b78d87a4a301147f351e8b7a48fa`、`auto-firmware-review @ 37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1`
- 环境 macOS 系统 Python 3.9.6、Reviewer API 0.28.0、VSOCK、无 NIC Linux Device Service API 1.99.1、Cardputer ADV QEMU

## 结论

macOS Reviewer 通过受限 VSOCK 使用 Linux Device Service 对同一份原版 `CardputerDict ADV 0.5.0` 执行两次标准 `saved_snapshot` 复审。允许策略下，固件完成验证服务器证书的 HTTPS 下载，向 SD 写入 10,605 字节 MP3，并产生 84,992 字节 I²S PCM。禁止策略下，DNS 和校时成功，HTTPS 尝试被拦截，复审返回明确的策略拒绝状态。两轮均释放租约和会话 Flash。

## 关键证据

- 缺失和错误认证各返回 HTTP 401，四个越出代理授权范围的请求返回 HTTP 403。
- 两轮复审提交均返回 HTTP 202。允许轮终态 `done / SIM_VERIFIED`；禁止轮终态 `manual_review / SIM_PARTIAL / E_CARDPUTER_PRONUNCIATION_POLICY_DENIED`。
- 分别回读每轮 Reviewer ZIP 和 Device Service ZIP。两份 ZIP 内的 PCAP 逐字节相同，允许轮的 PCM 也逐字节相同。
- Linux 命名空间和会话进程退出，macOS Reviewer 和 VM 停止，宿主监听关闭。Burner 提交、生产流量和物理硬件为 `NOT RUN`。

## 文件

- [执行报告](report.md)
- [结构化记录](run.json)
- [脱敏运行证据及原始回执哈希](evidence/macos-linux-vsock-adv.summary.json)

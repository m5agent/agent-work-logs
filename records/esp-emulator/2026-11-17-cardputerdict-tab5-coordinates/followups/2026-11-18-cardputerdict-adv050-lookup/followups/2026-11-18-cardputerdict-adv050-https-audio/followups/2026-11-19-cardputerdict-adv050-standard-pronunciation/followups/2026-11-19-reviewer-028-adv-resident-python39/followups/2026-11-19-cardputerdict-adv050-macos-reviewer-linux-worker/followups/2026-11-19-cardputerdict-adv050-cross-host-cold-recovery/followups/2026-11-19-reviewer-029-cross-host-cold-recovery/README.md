# Reviewer 0.29 活动复审跨系统冷恢复复验

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PASS`（隔离持久卷，虚拟设备验证）
- 工作类型 `report`，承接 [0.28 活动复审冷恢复](../../README.md)
- 源码 `auto-firmware-review @ 69386c6a162a1c786d6745c46eaa330c14558d3c`、`esp-emulator @ c9ec0f274579b78d87a4a301147f351e8b7a48fa`
- 环境 macOS 系统 Python 3.9.6、Reviewer 0.29.0、认证 Virtio VSOCK、无 NIC Linux Device Service 1.99.1

## 结论

Reviewer 0.29.0 使用同一后端地址、认证配置与 SQLite，在同一 Linux worker 状态卷上完成 CardputerDict ADV 0.5.0 原版的活动审核冷恢复。实际保存快照请求依次返回 `202 → 409 → 202`。无宿主停机凭证时旧租约与 Flash 保留，验证凭证后两者释放。随后相同原版通过复审，取得 10,605 字节 SD MP3 和 84,992 字节 I²S PCM。

- 同一 worker 三次进程代次递增。旧网关日志和两次 API 回读所得 PCAP 逐字节一致。
- 宿主与来宾各有两笔匹配的 SNTP 指纹和一笔匹配的 TLS 指纹。新 Reviewer 和 Device Service 两份 ZIP 中的 PCAP 与 PCM 相同。
- 两台试验 VM 和所属转发退出，无活动租约。常驻 Linux 生产路由、真机、宿主断电和 Burner 提交属于 `NOT RUN`。

## 文件

- [执行报告](report.md)
- [结构化记录](run.json)
- [脱敏运行证据与原始回执 SHA-256](evidence/reviewer-029-cross-host-cold.summary.json)

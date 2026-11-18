# CardputerDict ADV 活动复审跨系统冷恢复

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PASS`（隔离持久卷，虚拟设备验证）
- 工作类型 `report`，承接 [跨系统原版复审](../../README.md)
- 源码 `esp-emulator @ c9ec0f274579b78d87a4a301147f351e8b7a48fa`、`auto-firmware-review @ 37d7675dced42b2b932c51d1ca21bbb8ccfdf7e1`
- 环境 macOS 系统 Python 3.9.6、Reviewer API 0.28.0、认证 Virtio VSOCK、无 NIC Linux Device Service API 1.99.1

## 结论

macOS Reviewer 对同一份原版 CardputerDict ADV 0.5.0 发起标准保存快照复审。活动网关、租约和初始抓包可见后，受测宿主确认旧 VM 停止。后继 Linux 使用同一独占状态卷，Reviewer 使用同一后端地址、认证配置和 SQLite 历史。

- 宿主停机凭证缺失时，原版重试返回 HTTP 409，旧租约、Flash、审核记录和旧 PCAP 保留。
- 同一后继启动接收精确只读凭证后，旧租约、Flash 和 Reviewer 创建意图全部释放，原网关日志与 PCAP 保持逐字节一致。
- 相同原版标准重试返回 HTTP 202，终态 `done / SIM_VERIFIED`。实测 10,605 字节 SD MP3、84,992 字节 I²S PCM，Reviewer 与 Device Service 的 ZIP 数据一致。
- 两台 VM 先后停止，两个桥接监听及宿主协议转发关闭，活跃租约归零。生产路由、Reviewer 0.29、真机和 Burner 提交均为 `NOT RUN`。

## 文件

- [执行报告](report.md)
- [结构化记录](run.json)
- [脱敏运行证据和原始回执哈希](evidence/cross-host-active-cold.summary.json)

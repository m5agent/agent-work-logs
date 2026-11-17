# StickS3 原版配网与隔离夹具对照

- 日期 `2026-11-17`
- 结果 `PARTIAL`（原版热点启动，关联和应用 HTTP 未验证）
- 类型 `hardware_test`（原生虚拟设备）
- 来源 StickS3 首次配网和按键触发验证
- 源码 `m5stack-esp-emulator @ bb91232a26aa91e9f0bcd8dbfb736940c934b55e`
- 环境 独立 StickS3 QEMU，闭环隔离网络，关闭外部 IP 后端

v0.2.4 作者应用以原字节配合其指定的引导和分区布局运行。无输入时原版进入配网页并发送 262 个热点信标。独立运行中，长按 B 2 秒没有改变首次配网画面。原版源码中的首次配网和设置里的退出循环属于不同路径。

同一原生运行时的 SDK 对照在按键和复位后均完成关联、DHCP 和 HTTP。原版未与当前固定测试对端建立连接，原版配网页 HTTP 和 STA 配网仍待验证。所有运行已清理，未提交 Burner。

- [原版及构建上下文复现](report.md)
- [结构化记录](run.json)
- [同会话数据与清理摘要](evidence/portal-validation-summary.json)

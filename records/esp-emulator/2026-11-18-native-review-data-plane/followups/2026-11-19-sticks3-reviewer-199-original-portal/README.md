# StickS3 原版配网保存快照复审

- 日期 `2026-11-19`（UTC+08:00）
- 结果 `PARTIAL`；同一虚拟设备的本地配网 `PASS`
- 工作类型 `report`，延续原版 StickS3 热点配网的 Device Service 验证
- 固件 StickS3-Claude-Codex-Assistant v0.2.4
- 环境 macOS ARM64，原生 Xtensa QEMU，Device Service API 1.99.0，Firmware Review API 0.27.0

## 结论

按 `saved_snapshot` 重试原版应用，审核器创建唯一 StickS3 租约。来宾先启动热点、提供配网页面，接受原版 `/wifisave` 表单后切为 STA，并完成第二段 DHCP 和 ARP。审核记录 `checks.ap_provisioning.status=PASS`，整体保留 `manual_review / SIM_PARTIAL / E_NETWORK_PARTIAL`。云端助手为 `NOT RUN`，Burner 未提交。

## 关键证据

- 使用原版 2,907,680 字节应用和同工具链启动前缀。两份输入和组合 Flash 均核验 SHA-256。没有重新构建应用。
- 独立回读终态 PCAP，按顺序复原两段 DHCP、两条 HTTP 200 和 STA 的 ARP 回包。两份响应正文分别为 5,448 与 5,347 字节，哈希与审核报告相同。
- 配网完成后读取同一来宾的 Flash。NVS 有 4,344 字节变化，应用字节完整保留。结束后释放 peer、Flash 和唯一租约。
- 第一次在启动上下文绑定字段不完整时以 `E_APP_ONLY_BASE_MISMATCH` 停在受理阶段，零来宾。补齐配置后用同一应用重跑。

## 文件

- [执行报告](report.md)
- [结构化记录](run.json)
- [脱敏后的同会话协议与 Flash 摘要](evidence/same-guest-summary.json)

本次是复验。源码补丁和回滚不适用。云端助手、物理设备与 browser-WASM 均未执行。此前的 Device Service 直测覆盖同会话复位和已配网 Flash 冷重载，本记录只对本次审核入口测得的行为作结论。

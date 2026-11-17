# Cardputer ADV 原版 SkyCompass 离线 DNS 和授时

- 日期 `2026-11-17`
- 结果 `PARTIAL`（本地授权夹具通过，原版公共 HTTP 未验证）
- 工作类型 `code_change`
- 版本 原生 Device Service `bb91232a`，审核服务 `952ba18`
- 环境 隔离原生 Cardputer ADV、同一会话的虚拟网络和审核服务

原版 SkyCompass Satellite 3.6 从实际配网界面完成四步设置，经 DHCP、DNS 和 SNTP 两次收到夹具响应，并报告指定 UTC。整单保留 `SIM_PARTIAL / E_NETWORK_PARTIAL`。审核从同一个会话核对了来宾读回、已结束的 pcap 和响应包的指纹。

- [报告与判定](report.md)
- [结构化登记](run.json)
- [冻结包原版复审回执](evidence/frozen-review-summary.json)

原版字节通过 SHA 对照，隔离租约归零，未提交 Burner。无真实硬件或公网应用数据访问。

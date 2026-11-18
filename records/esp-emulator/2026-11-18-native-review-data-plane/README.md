# 原生固件审核数据面补齐

- 日期 2026-11-18
- 结果 PARTIAL。原版的本地配网、SD 缓存断言与 Dial 画面路径通过，尚有未完成的原版行为。
- 工作类型 code change
- 来源 固件审查 P0 输入、存储、网络
- 模拟器 a0fa14ae26f047fe4bef2c53681f9ea61b13eb8e
- 审核器 959c8fce00b918d62309f031eceaca4b0f41b113
- 环境 macOS 隔离 Device Service 和审核器。来宾证据为 virtual-device validation。

StickS3 原版从配网页切到本地 STA。CardputerDict 原版在画面相同的情况下验证缓存写入。Dial 原版恢复画面和默认节奏整周输入。SPI 接收 DMA 修复保留正常 SD 读写，ADV 原版 MP3 播放回归通过。

- [技术记录](report.md)
- [结构化记录](run.json)
- [StickS3 原版抓包与数据面摘要](evidence/sticks3-portal-station-summary.json)
- [StickS3 审核报告摘要](evidence/sticks3-reviewer-summary.json)
- [Dial 和 ADV MP3 原版回归](evidence/dial-mp3-combined-summary.json)
- [CardputerDict 原版缓存复审](evidence/cardputerdict-final-summary.json)
- [EMBER 隔离原版回归](evidence/ember-isolated-regression-summary.json)
- [SPI DMA 探针和 NC1020 边界](evidence/s3-gpspi-idle-rx-summary.json)
- [Reviewer 活跃会话创建恢复](followups/2026-11-18-reviewer-active-create-recovery/README.md)
- [Device Service 与 Reviewer 双重启恢复](followups/2026-11-18-reviewer-device-double-restart/README.md)
- [审核会话具名出口网关恢复](followups/2026-11-18-reviewer-named-gateway-restart/README.md)
- [外层网关监督进程中断后的审核恢复](followups/2026-11-18-reviewer-gateway-outer-loss/README.md)
- [具名网关启动交接中断恢复](followups/2026-11-18-reviewer-gateway-startup-handoff/README.md)

全部 dry-run 未提交 Burner。真机、物理 RF 和声学输出为 NOT RUN。

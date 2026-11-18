# Linux worker 冷容器重启与隔离准入

- 日期为 2026-11-18。工作类型为 infra baseline。
- 结果为限定 PASS，包括空闲 worker 重启、已完成会话的持久证据读回和隔离准入负控。
- 环境为独占 Linux arm64 容器、Device Service 1.89.0、Reviewer 0.21.0 和 Cardputer ADV 本地 STA SDK 夹具，验证类型为 virtual-device validation。
- 来源是[保存快照与原生审核数据面的后续验证](../../README.md)。本轮无对应 issue、固件发布或补丁。

在共享同一测试状态的三个新容器中，worker 身份保持一致，代数依次 1、2、3。前两代各有一单本地 STA 夹具通过指定应用断言，后代通过 API 逐字节读回先前详情、保存 ZIP 和已封存 pcap。第三代缺少 namespace 能力，创建会话返回 503，零新租约，两单历史均保留。

[完整报告](report.md) · [验证清单](run.json) · [结构化回执](evidence/linux-worker-idle-restart-summary.json)

两单整单结果仍为 E_NO_FRAME。运行中 guest 重连、跨物理主机、实际常驻部署和原版 ADV 发音均未在本实验执行。

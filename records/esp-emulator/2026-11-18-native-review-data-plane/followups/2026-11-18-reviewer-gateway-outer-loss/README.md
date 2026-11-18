# 外层出口网关监督进程中断后的审核恢复

2026-11-18，隔离 ARM64 Linux 原生虚拟设备验证。使用同一份 CardputerDict 0.6.4 原版及存储种子，对照外层监督进程单独退出，以及外层退出后设备服务与审核服务均重启。此前的具名网关恢复已覆盖两套服务重启时外层监督进程仍可协作清理的情况。

旧版两组均保留受影响的命名空间、虚拟网线、NAT 表、Flash 和租约。在单独终止外层的旧版组，来宾退出后网络资源仍未释放。

Device Service 1.98.0 的两组均在首次查询会话详情前自动回收旧运行时及网关资源，保留同会话证据与独立网关。标准 Retry 均启动新同原版会话并通过合成 SNTP 与 TLS ClientHello 传输验证；发音审核仍为 `manual_review / E_CARDPUTER_PRONUNCIATION_PARTIAL`。

[报告与复现](report.md) · [结构化记录](run.json) · [旧版双场景回执](evidence/named-outer-loss-baseline.summary.json) · [新版双场景回执](evidence/named-outer-loss-candidate.summary.json) · [此前具名网关恢复](../2026-11-18-reviewer-named-gateway-restart/README.md)

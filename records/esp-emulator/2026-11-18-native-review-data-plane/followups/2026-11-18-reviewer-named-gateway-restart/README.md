# 审核会话的具名出口网关中断恢复

- 日期 2026-11-18（UTC+08:00）。
- 范围 Linux 具名网络命名空间、veth 与 NAT 回收，原版 CardputerDict 的类型化审核路径，以及 macOS Core2 既有恢复回归。
- 环境 无外部网卡的独立 ARM64 Linux 虚拟机与独立原生 macOS Device Service。

Linux 内核对照通过真实挑战请求和回包验证源地址转换。清理后，受测的命名空间、两端虚拟链路和 NAT 表均消失，独立实验对端仍可用至其单独清理。macOS 原版 Core2 标准重试四向盘面通过。

先启动 Device Service 的同原版 Linux A/B 已完成。旧版在观测窗口内仍持有该会话的网关、运行时和租约。新版按两种启动顺序均在标准重试前自动清理，并保留同会话 26 包抓包和独立会话。两次重试均创建新的同原版会话，合成对端传输验证通过，综合发音审核保持 `manual_review / E_CARDPUTER_PRONUNCIATION_PARTIAL`。

[报告与复现](report.md) · [结构化记录](run.json) · [Linux 内核对照](evidence/primitive.summary.json) · [具名网关 A/B 与启动顺序](evidence/linux-named-gateway-paired-restart.summary.json) · [原版 macOS 控制](evidence/macos-core2-control.summary.json) · [此前无具名网关的双服务恢复](../2026-11-18-reviewer-device-double-restart/README.md)

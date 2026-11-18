# Linux 审核网关的关闭 stdin 回归

- 日期为 2026 年 11 月 19 日（UTC+08:00）。
- 结果为虚拟设备验证 PASS。基线启动失败已复现并保留。
- 工作类型为代码修复和原版固件 dry-run。
- 问题来源为 Linux 审核网关的启动回归。
- Device Service 基线为 `1939e39885d3cffe74f01576182bfa28c6148dd2`，修复为 `4216d548477d0b7a52b72f5e07dd07d98d7e8d63`。
- 环境为无网卡 Linux ARM64 VZ，运行 Device Service API 1.99.0、Reviewer 0.27.0 和初代 Cardputer 的原生 QEMU 路径。

外层网关的 stdin 关闭时，基线将 FD 0 传给内层，保存快照重试随后报告 `E_SIM_STARTUP_FAILED`。修复后内层收到 guard FD 5 和 permit FD 3。原版 CardputerDict 0.6.4 在允许场景缓存了 10,605 字节 MP3，并产生 84,992 字节数字 PCM。拒绝场景返回独立的 `E_CARDPUTER_PRONUNCIATION_POLICY_DENIED`。

两次候选试跑均校验了审核器和 Device Service 的证据 ZIP，确认同会话 PCAP 逐字节一致，并释放了租约、可写 Flash 和临时网关资源。关闭 stdin 的条件由测试入口注入并留证。

[执行报告](report.md) · [结构化记录](run.json) · [脱敏证据摘要](evidence/linux-gateway-closed-stdin.summary.json)

物理设备和常驻 worker 接入均为 NOT RUN。Burner 未提交。修复源码以提交标识定位。

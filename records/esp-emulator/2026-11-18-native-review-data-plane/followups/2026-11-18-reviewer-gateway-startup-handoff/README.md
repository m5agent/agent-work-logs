# 具名出口网关启动交接中断恢复

2026-11-18，隔离 Linux ARM64 原生虚拟设备验证。使用 CardputerDict 0.6.4 原版和同一存储种子，检查外层具名网关在内层创建前、以及内层已创建但未提交启动交接时中断。

Device Service 1.98 的两种路径分别暴露了资源滞留和外层退出后仍启动来宾。初版交接保护挡住了迟到启动，但资源直到 61.310 秒才回收。最终 Device Service 1.99 在内层创建前中断的对照中，于 2.436 秒自动回收并完成标准同原版 Retry。

1.99 在已创建内层但未提交交接的场景也通过。旧内层还持有锁时保留原资源，恢复后发现交接未提交并退出，未启动旧来宾，5.186 秒完成回收。两组普通 Retry 都创建新同原版会话，合成 SNTP 和 TLS ClientHello 传输通过，发音审核保持 PARTIAL。

[报告与复现](report.md) · [结构化记录](run.json) · [最终双场景回执](evidence/linux-named-gateway-handoff-release.summary.json) · [此前外层网关中断恢复](../2026-11-18-reviewer-gateway-outer-loss/README.md)

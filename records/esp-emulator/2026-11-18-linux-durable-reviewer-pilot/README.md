# Linux 持久审核试验

- 日期 `2026-11-18`
- 结果 `PARTIAL`
- 工作类型 `infra_baseline`
- 问题来源为原生审核 Linux worker 持久化验收
- 源码采用 Device Service `a729e24b1e4724b783ab2d59eec689cfdfeb24b3` 与 Reviewer `a295e0173a0e3157c120de8ba6fcec128aa665c1`
- 环境为无虚拟网卡的隔离 Linux ARM64 来宾，使用专用 VirtioFS 卷与初代 Cardputer 的 QEMU 原生路径

持久卷通过跨进程 SQLite WAL、写入竞争和文件锁验证。标准保存快照重试启动了原版 CardputerDict 0.6.4，应用发起 SNTP 和 TLS ClientHello。磁盘可用空间低于 4 GiB 时试验停止，审核没有运行到终态。

[执行报告](report.md) · [运行记录](run.json) · [有界证据](evidence/pilot.summary.json)

本次未完成旧任务及 ZIP 的冷启动回读，未接入可信 HTTPS 服务或验证 PCM。没有实机烧录或 Burner 提交。

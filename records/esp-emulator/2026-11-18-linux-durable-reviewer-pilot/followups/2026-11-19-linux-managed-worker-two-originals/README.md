# 受管 Linux worker 重启与两份原版固件审核

- 日期 `2026-11-19`
- 验证方式为原生 virtual-device validation
- A2 两份原版审核与历史重读 `PASS`，最终有序停机 `FAIL`
- A3 两代有序停机、ADV、Core2 复跑与审核历史重读 `PASS`，保留首次 Core2 `SIM_PARTIAL`

独立 macOS Reviewer 0.29.1 通过认证 VSOCK 桥，把 Cardputer ADV 的 CardputerDict 0.5.0 和 Core2 的 2048 交给无网卡 Linux ARM64 中的 Device Service 1.99.3。标准保存快照审核中，ADV 录得 84,992 字节有效 PCM，Core2 的上下左右各两次滑动均通过棋盘状态断言。Worker 换代后仍可读取原证据。Reviewer 单独退出再打开同一数据库后，两条任务和 36 条事件保持一致。

A2 第二代最终停机时，来宾读到截断的生命周期命令文件，未发出完整关停凭证。控制器确认中止来宾并锁定此卷的正常重启。两份任务的原始成功回执与这次停机故障均已保留。

A3 使用每一代单独封存的停机命令。两个 Linux 来宾均完成服务排空和正常退出，关停后桥接端点撤下，持久卷锁释放。第一代的 ADV 已停止会话在第二代逐项重读通过。Core2 在同一第二代的首次测试有七次动作通过，复跑同一原版与参数后八次全部通过。首次结果与原证据完整保留。

[执行与复核](report.md) · [运行索引](run.json) · [脱敏机器可读证据](evidence/linux-managed-two-originals.summary.json) · [Linux durable pilot](../../README.md)

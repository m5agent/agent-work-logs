# Core2 活跃会话运行器退出后的隔离与重试保护

- 日期为 `2026-11-19`，原生 virtual-device validation。
- 隔离与重试保护验证 `PASS`，原审核保留 `service_error / SIM_PARTIAL / E_SERVICE_RESTART`。
- 在独立新卷的一个真实活跃 Core2 会话上终止 VZ 运行器，控制器进入隔离，监听撤下；重启 Reviewer 后 Linux 就绪为 503、普通重试为 409。
- 同一创建意图、租约条目和 16 MiB 工作 Flash 继续保留。实时设备清理为 `UNCONFIRMED`，可信冷恢复与资源释放均未执行。

[报告](report.md) · [运行索引](run.json) · [有界证据](evidence/core2-active-runner-exit.summary.json) · [此前响应丢失恢复](../../README.md)

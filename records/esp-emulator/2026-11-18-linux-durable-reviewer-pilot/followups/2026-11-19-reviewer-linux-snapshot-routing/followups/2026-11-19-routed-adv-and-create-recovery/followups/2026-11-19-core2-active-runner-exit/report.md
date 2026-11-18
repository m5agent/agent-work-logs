# Core2 活跃会话运行器退出后的隔离与重试保护

本轮使用独立的新 Linux 虚拟机卷和专用试验角色，源码固定为 Reviewer `b9426a2d8a88338d95346ed9b93b0eaf0893cb9a`（0.30.0）与 Device Service `2a7f979c0c7e67420d8b790a3cfdb692702abf05`（1.99.3）。原版 Core2 2048 应用为 505,760 字节，原 BIN、启动依据和初始 Flash 摘要均固定。此前正常代次和恢复记录保持原样。 [先前记录](https://github.com/m5agent/agent-work-logs/blob/a791b691ff7c05811aef9b469a96eaa01daaecdc/records/esp-emulator/2026-11-18-linux-durable-reviewer-pilot/followups/2026-11-19-reviewer-linux-snapshot-routing/followups/2026-11-19-routed-adv-and-create-recovery/report.md)

确认真实 Linux worker 中只有一个活跃租约、创建意图已绑定且 2048 画面可读后，暂停自有 Reviewer 以固定观察点。按匹配该检查点的操作回执，单独对试验 VZ 运行器发送 SIGKILL。控制器和桥随后退出；控制器状态为 quarantined，端点记录为 uncertain。接着终止暂停的 Reviewer，用相同源码、配置依据和 SQLite 文件重开，以检查启动恢复和普通重试的保护行为。

| 环节 | 结果 | 观测 |
| --- | --- | --- |
| 终止前原版会话 | PASS | 一个真实活跃租约和同一绑定创建意图，运行中 ZIP 的八个清单载荷验证通过，实际棋盘可读 |
| 运行器异常退出 | PASS（故障注入） | 运行器、控制器和桥退出，宿主 TCP 与 Unix 监听不可达；只有启动事件，没有正常停止或强制停止确认回调 |
| Reviewer 重开 | PASS（保护行为） | Linux 就绪返回 503 worker_unavailable，恢复事件保留 device_service_unavailable 待处理项，原任务保持 service_error / E_SERVICE_RESTART |
| 普通重试 | PASS（拒绝） | 返回 409，原有一个绑定意图与一条任务继续保留，主后端哨兵请求为零 |
| 持久证据 | PASS | 原会话元数据、租约条目与工作 Flash 留存；16 MiB 工作 Flash 与终止前 ZIP 逐字节相同，其中原应用在 0x10000 的 505,760 字节精确匹配 |
| 同卷普通启动 | PASS（拒绝） | 控制器预检拒绝未确认的旧卷；卷锁已释放，隔离状态保留，临时角色卸载，旧试验卷保持原样 |

本轮旧 Unix socket 节点仍保留，监听已不可达。没有可信正常停止标记或冷恢复授权标记。独立复核重新打开终止前 ZIP，核对全部八个载荷的 CRC、长度与 SHA-256，读取 SQLite 中同一任务、绑定意图和待处理恢复事件，再直接比对隔离卷中的整份工作 Flash。设备服务不可达，卷中的租约条目和文件作为待处置状态保留。 [完整有界证据](evidence/core2-active-runner-exit.summary.json)

验证范围为自有 VZ 运行器进程退出后的保守隔离和重试拒绝。实时设备清理为 `UNCONFIRMED`，可信冷恢复以及旧租约、Flash 的释放均为 `NOT RUN`。卷级崩溃恢复、主机操作系统重启、主机断电、物理硬件、浏览器 WASM、生产变更与 Burner 提交均为 `NOT RUN`。原始卷、固件、Flash、ZIP、数据库、进程和端点标识留在私有证据存储。

# ESP Emulator 本地 QEMU restart re-attach

- 日期：`2026-10-24`
- 结果：`PASS`（virtual-device infrastructure）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`22c9564a3c55e543b40d964f4a8ea27e2074073b`
- 结果版本：`b31c3ab6d827b7e2a7199e3e30e75952fe4eaa20`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40056119661>
- 环境：macOS Apple Silicon；真实 StickS3 QEMU；Device Service；Python 3

## 结论

Device Service 现在可以在重启后安全接管**仍然运行且 ownership 可证明**的
本地 QEMU：

- persisted PID 必须匹配同一 `ps -o lstart=` start-time；
- 当前 command line 必须包含本 session 的 QMP socket；
- QMP 必须可连接；
- `query-status` 必须返回 `running`；
- 新 worker generation 必须成功重建本地 lease。

任一项不成立时，session 被恢复为 `failed`、`interrupted=true`，并记录显式
错误；不会只凭 PID 把进程当成自己的。

成功接管后的 session 标记为：

```text
state=running
restored=true
interrupted=false
reattached_process=true
recovery_scope=qemu-control-plane
```

真实服务重启测试中，只对 Device Service PID 发 SIGKILL，StickS3 QEMU
继续存活；第二代服务在同一状态目录接管同一 QEMU PID，恢复 generation 2
lease，随后 `stop` 清理了 QEMU。live `1/1 PASS`。

## 关键证据

- 本地平台套件：`289/289 PASS`；
- Device Service：`82/82 PASS`；
- targeted reattach：`1/1 PASS`；
- live service restart：`1/1 PASS`；
- GitHub Actions：`Ran 289 tests`、`OK (skipped=2)`，两个 job 均成功；
- OpenAPI：`1.18.0`；
- source evidence SHA256：
  `2d7d70727fbf5502273fbac7008cb3863d5e87f41f80104246125ffdc1fa47c9`。

## 文件

- `report.md`：ownership 设计、live 执行、边界和回滚；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合结果。

源码证据：
<https://github.com/m5agent/m5stack-esp-emulator/blob/b31c3ab6d827b7e2a7199e3e30e75952fe4eaa20/tests/network/worker_reattach/evidence-2026-10-24-reattach-pass.json>

## 未覆盖项

- companion HTTP/BLE helper 连续接管；
- evidence stream / pcap 写入进程连续接管；
- Tab5 和独立 network lane re-attach；
- paused QEMU、跨主机进程和多机调度；
- 独立 job executor；
- 物理硬件验证。

# ESP Emulator Core2 active-stop 与连续恢复

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：P0 Core2 生命周期里程碑中尚未验证的 process-stop/teardown
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`7da51aa915567cb681e64eb1d0ffff451393bf7a`
- 测试与证据提交：`3621301bef264447f79812530e157d3090826e5f`
- CI 证据提交：`c36b7907b929363374fe3d2e0ba5d486a6d4fdc8`
- 环境：macOS Apple Silicon；Python 3；真实 Device Service `/api/v1`；QEMU

## 结论

Core2 `core2-native-hci` 的 active-stop/recovery 门禁连续通过 `3/3`。
每个 session 都在 HTTP/BLE companion 仍活跃、BLE peer 仍处于 120 秒
linger 窗口时删除。

三次 DELETE 均在约 `0.15–0.36s` 内完成：

- final state 为 `stopped` 且无错误；
- HTTP/BLE companion 进入 `terminated`；
- BLE peer 与 QEMU PID 均被回收；
- worker active lease 降为 `0`；
- 下一次 session 能重新启动并再次完成 frame/QOM、WiFi DHCP/HTTP、
  公网 DNS/HTTP、外部 NUS GATT、pcap 与 evidence。

## 关键证据

- 测试：`run_service_teardown.py --attempts 3`；
- 结果：`3/3 PASS`；
- 每个 session 的停止耗时：`0.359s`、`0.222s`、`0.154s`；
- firmware、ELF、QEMU、runner、Device Service、accelerator 与 BLE limits
  在首个 lease 前冻结，运行期无漂移；
- 平台测试：`411/411 PASS`；
- 文档契约：`22/22 PASS`；
- catalog、profile、runtime coverage 和 project snapshot：`PASS`；
- GitHub Actions `40146597625` 与证据提交 run `40146679013` 均通过两个 job。

## 文件

- `report.md`：生命周期验证过程、边界和回滚；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- bit-exact Espressif BT controller/baseband；
- 物理 cache/PSRAM timing；
- 长时并发与吞吐；
- active-stop 之外的其他进程停止/teardown 时序；
- 跨主机 QEMU migration、物理 RF 或真机验证。

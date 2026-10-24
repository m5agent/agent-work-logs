# ESP Emulator code/document inventory and one-page handoff

- 日期：`2026-10-25`
- 结果：`PASS`（docs/contract scope；运行功能矩阵未重跑）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`0e3a913207dd8772d497a8e4dfb5580ba597f5b3`
- 结果版本：`61204890a1442ea6b88652fd5da53d678a8a826e`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40143120598>
- 环境：macOS Apple Silicon；Python 3；Node 20；无物理硬件

## 结论

项目当前状态已经从“散落在顶层状态、专题页、设备 README、case README 和
历史 evidence”整理为可分层阅读的入口：

- `project-status.md` 顶部新增一页式交接，明确最近闭合项、当前实现项、
  后续 P0、已不应再写成 TODO 的能力和真机边界；
- Backlog 与工作流执行顺序改为以当前 companion continuity 为首项；
- 新增 `tests/README.md`、`tests/network/README.md` 和 `patches/README.md`
  总索引，并纳入文档契约；
- 自动项目快照新增代码/文档规模、最大工具模块、可执行测试、evidence、
  补丁组和 Markdown 页面统计；
- 修正多个过期结论，包括“四个公开固件功能未运行”“S3 WiFi 只有 Open”
  以及 Core2 仍停在“20 轮/RSS REVIEW”的描述。

本文档整理没有改变 QEMU/controller 数据面，也没有重跑功能矩阵。它验证的是
源码索引、文档一致性、链接、生成快照和平台契约。

## 当前工作

当前实现门禁是 `SVC-01` / `NET-04` companion continuity：

- `DeviceSession.reattach()` 已恢复 QEMU PID/start-time、QMP ownership 和
  running 状态；
- controlled HTTP fixture 与 BLE `_hci_probe` 仍只保存在进程内；
- 下一步需要持久化 companion ownership、端点、PID、日志 offset 和生命周期，
  在重启后安全 adopt 或幂等重建；
- 必须扩展到 unified StickS3 restart fixture，验证重启后 HTTP、NUS GATT、
  serial/network/peer evidence 和 cleanup 连续。

## 剩余待办

1. `SVC-01` / `NET-04` companion continuity，随后是真跨主机 QEMU
   executor/reattach、NAT/跨子网 discovery、跨主机 idempotency 和生产调度。
2. `FW-01/02/03` 运行态 ACL/许可、真机 security/key 流程、真实
   key/cloud 和更多固件族。
3. `RUNTIME-02/03/04` C6 Zigbee、Core2 legacy I2C routing 和 ATECC608。
4. `CORE2-02` 长时吞吐/teardown、bit-exact controller、物理 cache/PSRAM。
5. `HW-01` 代表设备同固件 SHA 的真机验证。
6. `SVC-02/03`、`TAB5-01`、`UI-01`、`CZ-01`。

## 关键证据

- 平台测试：`396/396 PASS`；
- 文档契约：`21/21 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`；
- compileall、Ruff fatal checks、`git diff --check`：`PASS`；
- GitHub Actions `platform-contracts` 与 `network-namespace-policy`：
  `PASS`；
- 源码提交：`61204890a1442ea6b88652fd5da53d678a8a826e`。

## 文件

- `report.md`：整理范围、纠偏、验证和剩余边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `patches/`：不适用，改动均在源码仓库提交 `6120489`；
- `code/`：不适用，入口是源码仓库 `tests/README.md` 和
  `patches/README.md`。

## 未覆盖项

- 完整 QEMU/外设功能矩阵本轮未重跑；
- companion HTTP/BLE/evidence continuity 未实现；
- physical hardware、RF、功耗、电气、声学和光学：`NOT RUN`；
- CI 两个 job 已在结果提交上通过；它不替代未运行的功能矩阵。

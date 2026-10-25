# ESP Emulator current-code and documentation freshness audit

- 日期：`2026-10-25`
- 结果：`PASS`（docs/contract scope；功能矩阵未重跑）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`2dd44b2b78fb3463ff2be9cb36321b19e93f49d3`
- 实现提交：`dc1f92fd81a7c932b7d2dcb8b0b0dc13ad4c30fb`
- 结果版本：`7aa46c6459e205777e48c49f50a3abf23cd292bf`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40162620429>
- 环境：macOS Apple Silicon；Python 3；Node 20；无物理硬件

## 结论

当前代码、已交付能力和待办已重新校准到 worker partition QEMU 里程碑之后：

- 顶层 README 只保留当前能力摘要，长验证流水移回状态、专题和 evidence；
- `project-status.md` 新增“当前工作与下一门禁”，明确每项能做什么、下一步
  和不能继承的边界；
- `project-backlog.md` 压缩已完成 dependency 流水，只保留仍在开放的
  `NET-04`、`CORE2-02`、固件安全、运行时缺口和后续专项；
- worker partition 结论明确区分 worker-owned QEMU process、QEMU 内
  guest/controller、`qemu-unified` companion 和 worker 未拥有的外部 side effect；
- 自动项目快照新增文档职责分布和“复核日期早于事实日期的非历史页”审计；
- 文档契约新增索引重复链接、权威页重复长行和新鲜度审计结构检查；
- 清理了两个真实 Ruff `E9/F` 问题：无占位符 f-string 和未使用变量。

本次没有重新执行 QEMU 功能矩阵，也没有把文档整理当成新的设备功能 PASS。

## 当前工作与待办

下一项 P0 是 worker-local `qemu-unified` partition/companion lane：

1. 同一 session 内运行 HTTP fixture、BLE peer、pcap 和 guest；
2. worker→control 断网后 fence 整个 runtime；
3. 验证 QEMU、companion、PID、namespace 和磁盘 side effect 一起停止；
4. attempt 2 启动新实例并完成 evidence；
5. 继续补物理跨主机 executor/reattach、跨主机幂等和任意 NAT traversal。

其他开放项只由[项目 Backlog](https://github.com/m5agent/m5stack-esp-emulator/blob/7aa46c6459e205777e48c49f50a3abf23cd292bf/docs/project-backlog.md)维护，
包括 Core2 物理/controller 边界、固件运行态安全、C6 Zigbee、Core2 legacy
I2C、ATECC608、真机同路径、Tab5、视觉和 CardputerZero。

## 关键证据

- 平台测试：`447/447 PASS`；
- 文档契约：`33/33 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot：
  `PASS`；
- Ruff `E9/F`、compileall、`git diff --check`：`PASS`；
- GitHub Actions `platform-contracts` 与 `network-namespace-policy`：`PASS`；
- 实现提交：`dc1f92fd81a7c932b7d2dcb8b0b0dc13ad4c30fb`；
- 验证台账与生成快照提交：`7aa46c6459e205777e48c49f50a3abf23cd292bf`。

## 文件

- `report.md`：整理范围、同步规则、验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `patches/`：不适用，改动在源码提交 `dc1f92f` 和 `7aa46c6`；
- `code/`：不适用，权威入口是源码文档测试和生成快照。

## 未覆盖项

- 完整 UIFlow2 外设矩阵：`NOT RUN`；
- 新的网络/worker 功能路径：`NOT RUN`；
- 物理跨主机、真机、RF、功耗、电气、声学和光学：`NOT RUN`；
- 文档日期审计只能提示复核候选，不能证明页面内容一定正确。

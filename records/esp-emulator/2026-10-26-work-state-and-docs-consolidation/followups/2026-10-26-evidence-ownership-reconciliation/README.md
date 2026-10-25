# ESP Emulator evidence-ownership and current-work reconciliation

- 日期：`2026-10-26`
- 结果：`PASS`（documentation/contracts）；firmware/QEMU functional rerun
  与 hardware validation 为 `NOT RUN`
- 工作类型：`report`
- 问题来源：用户指出多份文档仍像旧阶段快照，未结合后续 Core2 探针、
  runtime gap、网络/worker 和固件审查工作
- 源码版本：
  [m5stack-esp-emulator @ 1b923f8](https://github.com/m5agent/m5stack-esp-emulator/commit/1b923f83d6906545879e16262aaa3b3e10cc7c74)
- Base commit：`7bf311e67385552a6be5c2f610811421458e1e73`
- 环境：macOS arm64；Python 3.13.15；未启动 QEMU guest 或物理设备

## 结论

当前入口已经重新分层。README、项目状态、Backlog、工程交接、工作流和 QEMU
适配矩阵只描述稳定能力、调查假设、待办和不可继承边界；PASS 比例、轮次、
资源数值、哈希和逐项检查数回到验证台账、专题日期化证据或 evidence JSON。

本次重点修正了 Core2 最新纠错后的漂移源：上层页面不再重复 flash/IPC probe
的单次通过率；`profiles.json` 的 blocker 不再嵌入整串并发批次；
`platform/README` 的 Core2 历史流水压缩为当前可执行面与链接；
`code-map` 明确验证表是入口索引，不是当前验证快照。文档契约新增回归检查，
防止这些易漂移数字重新进入上层页面。

## 关键证据

- 本地平台测试：`500/500 PASS`；
- 文档领域契约：`40/40 PASS`；
- QEMU profile contract：`19/19 PASS`；
- compileall、Ruff `E9/F`、runtime coverage、peripheral catalog、QEMU
  profiles、project snapshot 和 `git diff --check`：PASS；
- 产品 CI：[40214948602](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40214948602)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS。

## 文件

- `report.md`：整理原则、改动、验证与边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：命令、提交、CI 和未覆盖项。

## 未覆盖项

- 本次只整理代码入口、生成配置与文档口径，没有修改 Device Service、QEMU
  或固件行为；
- 没有重跑 Core2 legacy UIFlow、flash/IPC、并发、长稳、网络或外设矩阵；
- `RUNTIME-03`、legacy 黑帧、timer/interrupt 根因、buffer controller、
  物理 PSRAM/cache、RF、电气和真机仍为开放或 `NOT RUN`。

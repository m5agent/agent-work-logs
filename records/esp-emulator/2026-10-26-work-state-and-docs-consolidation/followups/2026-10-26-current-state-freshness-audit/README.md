# ESP Emulator current-state and documentation freshness audit

- 日期：`2026-10-26`
- 结果：`PASS`（documentation/contracts）
- 工作类型：`code_change`（文档生成器和契约测试）
- 源码版本：
  [m5stack-esp-emulator @ 5f68d70](https://github.com/m5agent/m5stack-esp-emulator/commit/5f68d70f51f39eef82113f6836843ef5b996ef23)
- Base commit：`c9cd5a93c1ef2ac0046566299879ea69b6d478c9`
- 环境：macOS arm64；Python 3.13.15；Node 由 CI 覆盖；
  firmware/QEMU functional rerun 和 physical hardware `NOT RUN`

## 结论

本轮不是再增加一份状态摘要，而是修正了多份入口文档之间的事实源和新鲜度
关系：

- `project_snapshot.py` 不再把设备 catalog 的 `generated_at` 当成项目事实日期；
- 快照同时展示 catalog 日期、当前事实复核日期和最新 evidence 日期；
- 快照行数统计排除生成页自身，消除了“写一次后下一次仍判 stale”的自引用漂移；
- 所有权威页和委派页完成日期复核，`older_current=0`、`older_delegated=0`；
- README 删除 Core2 exact-time 地址和虚拟时间流水，保留稳定结论并链接状态/台账；
- UIFlow2 外设矩阵把完整基线修正为 `0036` stateful SSI 重建后的共享控制器
  回归，`0038` 明确只是 exact-time 诊断加 Core2 定向回归；
- Core2 native-HCI 文档把当前最大 reconnect 门禁收敛到 121 轮、122 拒绝，
  当前并发容量上限收敛到 8，不再保留“最多五实例”的旧边界；
- GDB/VHCI 页面继续明确标为 legacy/diagnostic，不进入规范产品路径。

## 关键证据

- 全平台测试：`510/510 PASS`；
- docs 契约：`43/43 PASS`；
- `runtime_coverage`、`peripheral_catalog`、`qemu_profiles`：PASS；
- `project_snapshot --write` 连续两次后 `--check` 仍 PASS；
- 生成快照日期：
  - catalog `2026-10-25`；
  - current fact `2026-10-26`；
  - latest evidence `2026-10-26`；
- 文档审计：`216` 个 Markdown 页面；权威页旧日期 `0`、委派页旧日期 `0`；
- compileall、selected Ruff `E9/F` 和 `git diff --check`：PASS；
- product CI：
  [40237507431](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40237507431)
  的 `platform-contracts` 与 `network-namespace-policy` 均 PASS。

## 文件

- `report.md`：根因、修改、验证、边界和回滚；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：验证、快照日期和 CI 汇总；
- `evidence/snapshot-facts.json`：该提交生成快照的日期、计数和审计摘要。

## 未覆盖项

- 本轮没有重跑 UIFlow2 全量或 Core2 长稳/并发功能矩阵；
- 没有重新生成 firmware/ELF/QEMU-bound functional PASS；
- `RUNTIME-03`、`Core2FactoryTest` 重跑和同 SHA 非空应用帧仍为 `OPEN`；
- 真机、RF、功耗、声学、光学、机械、物理 PSRAM/cache 和电气均为 `NOT RUN`。

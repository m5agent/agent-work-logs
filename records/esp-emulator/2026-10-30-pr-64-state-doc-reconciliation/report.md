# ESP Emulator 当前状态与文档矛盾收敛报告

## 背景

- 来源：公开仓库 PR #64，base `345c879c5a69bc1e0c03bbca66738592176c732e`
- 需求：多 agent 并发开发后，重新收敛本地/远端基线，并梳理文档中的状态矛盾
- 目标：让当前状态、执行队列、历史证据和任务编号使用一致口径，同时不触碰
  其他 agent 的未提交工作或不属于本轮的 worktree

## 结论

- 状态：`PASS`（documentation/contracts）
- 关键判断：矛盾主要来自历史 `OPEN` 与后续关闭结论并列展示，而不是运行能力回退
- 改动范围：9 个 Markdown 文档、1 个文档契约测试、1 个 stale-claim fixture

已统一的主要矛盾：

1. `RUNTIME-03`：当前已关闭 virtual-device normal-WDT stock startup；历史段落中的
   `OPEN` 明确标为关闭前阶段，setup/REPL 与任意应用继续由 `API-01` 跟踪。
2. `RUNTIME-06`：工作流台账从“进行中”修正为“已完成（virtual-device）”，与
   Backlog、项目状态和自动快照一致。
3. Core2 设备矩阵不再把已关闭的 startup reset/黑帧当作当前边界，改为列出
   setup/REPL、任意 factory application、应用路径 display completion 和物理等价。
4. 用户固件矩阵明确区分 `2026-10-26` hash-bound checkpoint 与 `2026-10-30`
   `0095` 后续关闭证据，不把新 PASS 回填历史计数。
5. `CORE2-01` 明确标为历史设计标识，当前执行、容量与物理等价任务统一使用
   `CORE2-02`。
6. `runtime-model-gap-register.md`、工作流台账、项目快照、Core2 native-HCI
   专题和 Core2 历史调查的复核日期已收敛到 `2026-10-30`。
7. 文档索引增加通用规则：证据/计划行描述该日期当时的事实，后续证据可关闭历史状态，
   但不改写原记录。

## 执行

并发基线：

- 从最新 `origin/main` 创建独立 worktree；
- 共享 checkout 中与本任务无关的未提交文件保持原样；
- 只暂存本轮 11 个显式文件，未使用 `git add -A`；
- PR scope 检查确认 `new_evidence_bytes=0`。

验证：

```text
test_docs_current_state_contract
test_docs_index_contract
test_docs_core2_runtime_contract
test_docs_firmware_security_contract
test_docs_network_worker_contract
=> 50 tests PASS

runtime_coverage.py --check       => RUNTIME_COVERAGE_OK
peripheral_catalog.py --check     => PERIPHERAL_CATALOG_OK
qemu_profiles.py --check          => QEMU_PROFILES_OK
project_snapshot.py --check       => PROJECT_SNAPSHOT_OK
check_pr_scope.py                 => PASS
git diff --check                  => PASS
```

新增契约会把 Backlog Task 状态与 `workstreams.md` 的同 ID 状态逐项比较，防止再次出现
`RUNTIME-06` 一类状态漂移；stale-claim 清单新增 5 条退役措辞。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| review | `PASS` | 权威页、历史页、用户固件矩阵和任务状态完成交叉对账 |
| delivery | `PASS` | PR #64 检查 4/4 PASS；merge `ab009167`；main CI `41014601243` PASS |
| build | `NOT RUN` | 文档-only 改动未构建固件或 QEMU |
| transport | `NOT RUN` | 未启动 guest 或服务会话 |
| device_response | `NOT RUN` | 未执行设备或外设 |
| data_behavior | `NOT RUN` | 未执行功能矩阵 |
| visual_or_physical | `NOT RUN` | 未做 framebuffer、光学、机械、RF 或电气验证 |

## 风险与回滚

- 风险：本次只修正文档口径；错误的历史 evidence 或运行行为不会被文档修正
  自动关闭。
- 回滚：revert merge commit `ab0091670b932796f5d04a5cac80d728cfada742`。
- 本轮未删除历史证据、未放宽运行阈值、未修改 QEMU 或固件。

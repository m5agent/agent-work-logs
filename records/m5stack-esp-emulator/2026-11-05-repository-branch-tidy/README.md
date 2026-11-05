# M5Stack Emulator 仓库整理：本地/远端分支与工作树清点

- 日期：`2026-11-05`（Asia/Shanghai）
- 结果：`PASS`（仓库引用层整理；未改 tracked 内容）
- 工作类型：`report`
- 问题来源：用户要求整理仓库，清理混乱分支；并说明其他 agent 的启动/运行性能与 Web 界面优化已并入 `main`
- 源码版本：[m5stack-esp-emulator @ 84b4f493](https://github.com/m5agent/m5stack-esp-emulator/tree/84b4f493)（含 PR #170 Unit 预览/本地控制修复）
- 环境：macOS arm64、git、GitHub CLI；无 guest 执行、无物理硬件

## 结论

仓库的“很乱”主要是**已合并分支没有回收**：本地 103 个分支中 79 个是可安全清理的遗留（70 个已完全合入 `main` 的 `integration/*`、`m5agent/*` 与 `backup/*`，9 个补丁等价/已被主线取代），远端 25 个非 `main` 分支全部是已合并 PR 分支或已被取代的工作分支。清理后：

- 本地分支：`103 → 26`（`main` + 2 个 `attic/*` 归档 + 23 个仍被外部工作树检出的分支）；
- 远端分支：`25 → 1`（仅 `main`）；所有删除的远端分支都有已合并 PR 或等价提交；
- 工作树登记：清掉 4 条失效（gitdir 已不存在）记录，移除 2 个 `<tmp>` 下干净的旧 detached worktree，`31 → 25` 条；
- 保留 12 个 tag（Pages 发布快照与 runtime tag）与 1 个旧 stash（WIP 快照，未破坏性处理）；
- 清理仓库根目录两个自 2026-10-21 起无进程绑定的陈旧 `qomdebug*.sock`；
- 四个生成/契约检查在清理后仍全部通过：`PROJECT_SNAPSHOT_OK`、`RUNTIME_COVERAGE_OK`、`PERIPHERAL_CATALOG_OK`、`QEMU_PROFILES_OK`。

剩余的 23 个本地分支全部仍被**外部工作树**检出（17 个 codex 工作树 + 7 个同级工作区/副本工作树，另有本仓库主检出），其中 18 个已合入 `main`、5 个未合并。它们不属于“孤儿分支”：删除前必须先退出并退役对应工作区，因此本轮保持原样并单独列出；是否清理由用户决定。

## 关键证据

- 构建或运行：无代码/构建变更；`main` 保持 `84b4f493`，tracked tree clean。
- 产物或部署：不涉及部署；未改 Pages、未改分支内容。
- 实机或服务执行：不涉及 guest/服务；用户 8787/8792 测试服务未被触碰。
- 日志、测量或协议：[audit-summary.json](evidence/audit-summary.json)（前后数量、分类、清理动作）、[deleted_local_merged.txt](evidence/deleted_local_merged.txt)（70 个）、[deleted_local_obsolete.txt](evidence/deleted_local_obsolete.txt)（9 个）、[deleted_remote.txt](evidence/deleted_remote.txt)（24 个；另手动删除 1 个）、[kept_worktree_branches.txt](evidence/kept_worktree_branches.txt)、[local_after.txt](evidence/local_after.txt)、[remote_after.txt](evidence/remote_after.txt)、[worktree-summary.json](evidence/worktree-summary.json)、[tags_after.txt](evidence/tags_after.txt)。

## 文件

- [report.md](report.md)：清理前后清单、逐类判定依据、验证与回滚。
- [run.json](run.json)：机器可读记录。
- `evidence/`：脱敏后的分支/标签/工作树摘要与删除清单（不含本地绝对路径或凭据）。
- `patches/`：不适用，未修改源码。
- `code/`：不适用，无 guest 程序。

## 未覆盖项

- 23 个外部工作树持有的分支未清理：需要先处理 `codex 工作树目录/*` 与同级工作区（退出/归档），本轮不代用户退役工作区。
- 1 个 stash 未丢弃：2026-11-03 的性能/页面 WIP 快照已不能直接 apply 到当前 `main`，保留以便人工判断，不做破坏性处理。
- 未执行 `git gc`：仓库对象包约 516 MiB 且多为 `main` 可达历史，回收收益有限，且多工作树共享对象库；留待用户要求时再评估。
- `.work/` 运行时缓存、`platform/.cache/`、`config-temp/`、`config.log` 未删除：属于本地运行/调试资产，可能有其他 agent 或服务在用。

## 后续收口

- [唯一 main 与 Chrome 兼容提交](followups/2026-11-05-main-only-closeout/)：`PARTIAL`，Chrome49/平台检查、离线保全与23工作树detach通过；源码PR与最终引用清理待执行。
- [PR171交付与唯一main终态](followups/2026-11-05-main-only-closeout/executions/2026-11-05-pr171-delivery/)：`PASS`，本地/远端均仅main；原目录、tag、stash和历史备份保留。

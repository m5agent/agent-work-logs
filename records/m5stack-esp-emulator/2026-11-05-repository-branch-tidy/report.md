# M5Stack Emulator 仓库整理报告（分支 / 工作树 / tag / stash）

## 背景

- 来源：用户 2026-11-05 提出仓库分支太多、需要整理；同时说明其他 agent 最近的
  启动/运行性能优化与 Web 界面改动已并入 `main`。
- 现象：本地 103 个分支、远端 28 条 `git branch -r` 记录，其中大量
  `integration/next*`、`m5agent/*` 已合并分支长期未回收；`git worktree list`
  含已失效登记与 `<tmp>` 旧工作树。
- 目标：在不丢失未合并工作、不改动 tracked 内容、不影响用户/其他 agent
  工作区的前提下，把“已合并/已取代”的引用回收，保留仍有用的归档与外部
  工作树状态，并给出可复核清单。

## 结论

- 状态：`PASS`（引用层清理完成；需要外部工作区配合的 23 个分支按计划保留）。
- 关键判断：
  1. 本地 103 个分支中，89 个已合入 `main`（含 52 个 `integration/next*`
     单元批次快照链、`m5agent/*` PR 分支与 `backup/*`），其中 70 个不在任何
     工作树中、可安全 `-d` 删除；19 个被外部工作树检出而保留。
  2. 13 个未合并本地分支中：4 个补丁已等价于 `main`（`git cherry` 全 `-`），
     2 个已被主线同功能提交取代（`backup/pre-rebase-camera-geometry` 与
     `m5agent/atoms3u-visual-host`），1 个是 PR #166 已合并的文档分支，
     1 个是 PR #19 已合并前的测试分支；另有 `m5agent/pages-system-browser`
     与部分 patch-equivalent 分支被外部工作树检出，保留。
  3. 远端 25 个非 `main` 分支全部对应已合并 PR 或被主线取代的工作分支
     （PR #19、#80、#166 等），删除不丢提交；删除后 `git ls-remote --heads`
     只剩 `main`。
  4. `local-history`（21 个 2026-10-21 的历史提交）与旧 `<tmp>` 工作树
     `units26-fix2` 的 detached 提交无法从 `main` 直接到达，按“保留归档”
     处理：建立 `attic/local-history`、`attic/units26-fix2` 两个本地归档分支，
     再移除对应工作树；不 push 到远端。
  5. 工作树：`git worktree prune` 清掉 4 条 gitdir 已不存在的登记；移除
     `<tmp>/fix-order`（提交与 `main` 等价）与 `<tmp>/units26-fix2`
     （干净、旧）两个 detached 工作树；外部 codex/同级工作区工作树未动。
- 改动范围：仅 git 引用/工作树登记与仓库根目录两个陈旧 socket；未修改
  `main` 内容、未修改任何 tracked 文件、未触碰用户服务端口。

## 证据

### 清理前后数量

| 项目 | 清理前 | 清理后 | 说明 |
| --- | ---: | ---: | --- |
| 本地分支 | 103 | 26 | main + 2 attic + 23 个外部工作树持有 |
| 远端分支（非 main） | 25 | 0 | 仅保留 `main` |
| 标签 | 12 | 12 | Pages 发布快照与 runtime tag，全部保留 |
| worktree 登记 | 31 | 25 | 4 条失效登记 + 2 个旧 `<tmp>` 工作树 |
| stash | 1 | 1 | 旧 WIP，保留未丢弃 |

### 删除清单与判定依据

- 本地已合并（70）：`integration/final`、`integration/next2..50`、
  `m5agent/*` 已合并 PR 分支、`backup/core2-before-rebase` 等。删除前均满足
  `git merge-base --is-ancestor <branch> main`。
- 本地未合并但确认过期（9）：
  - `backup/core2-before-rebase`、`m5agent/core2-capacity-boundary`、
    `m5agent/svc03-{execution-parsing,network-execution,qemu-wifi}`：
    `git cherry main <branch>` 全部为 `-`（补丁等价于主线）；
  - `backup/pre-rebase-camera-geometry`：主线已有同功能提交 `786a4e4d`
    （GC0308 geometry），且证据目录已在 `main`；
  - `m5agent/atoms3u-visual-host`：PR #80 已合并，`main` 已有
    `devices/esp32-s3/atoms3r-cam/` 等产物；
  - `m5agent/stackchan-smoothing-evidence`：已合入 `main`，仅因上游 tracking
    分支差异导致 `-d` 拒绝，改用 `-D`；
  - `local-history`：内容转存到 `attic/local-history` 后删除原名。
- 远端（25）：24 个按名单批量删除 + `m5agent/atoms3u-visual-host` 单独删除；
  全部为已合并 PR 分支或已取代工作分支。`git ls-remote --heads origin`
  复核只剩 `main`。

### 保留项

- 23 个外部工作树持有的本地分支（18 个已合入 `main`，5 个未合并：
  `m5agent/{core2-current-toolhash-rebind,core2-teardown-modes,fw01-runtime-acl,pages-system-browser,pr165-rollout-recovery-20261104}`）。
  这些工作树分别位于 codex 工作树目录与同级工作区；本轮不代用户退役,
  以其现有 gitdir 为准保留。
- `attic/local-history`、`attic/units26-fix2`：本地归档，不推送远端。
- 12 个 tag、1 个 stash、`.work/`、`platform/.cache/`、`config-temp/`、
  `config.log`：保留。

### 执行

- 环境：macOS arm64，仓库主检出 仓库主检出；Python 3.12 venv 仅用于
  生成契约检查；无 guest/QEMU/浏览器执行。
- 命令（要点）：

```bash
git fetch --all --prune --tags
git branch --merged main            # 89 个（main 除外）
git worktree prune                  # 4 条失效登记
git worktree remove --force <tmp>/fix-order
git worktree remove --force <tmp>/units26-fix2
git branch --merged main | ... | xargs -n1 git branch -d
git branch -D <9 个已核实过期分支>
git push origin --delete <24 个远端分支>   # 另单独删 1 个
PYTHONPATH=platform/tools python3 platform/tools/project_snapshot.py --check
PYTHONPATH=platform/tools python3 platform/tools/runtime_coverage.py --check
PYTHONPATH=platform/tools python3 platform/tools/peripheral_catalog.py --check
PYTHONPATH=platform/tools python3 platform/tools/qemu_profiles.py --check
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| 本地引用 | PASS | 103 → 26；删除项均先经 `--merged` 或 `git cherry`/主线同功能提交核验 |
| 远端引用 | PASS | 25 → 1（main）；`git ls-remote --heads` 复核 |
| 工作树登记 | PASS | 31 → 25；失效登记与两个旧 `<tmp>` 工作树已清，外部工作树未动 |
| 生成/契约检查 | PASS | snapshot/runtime coverage/peripheral catalog/qemu profiles 四项 `OK` |
| tracked 内容 | PASS | `git status` clean；`main` 仍为 `84b4f493` |
| 外部工作树退役 | NOT RUN | 需用户/其他 agent 先退出对应工作区，本轮不代操作 |
| stash/gc | NOT RUN | 保留 WIP 与对象包，不做破坏性回收 |

## 验证边界

- 本报告只证明 git 引用/工作树登记层整理；不证明被删除分支里的历史讨论、
  外部链接不再需要，也不代替 PR 作者对未合并工作的确认。
- 23 个外部工作树分支未清理，因此“分支完全归零”未达成；需要先退役
  codex/同级工作区。
- 远端分支删除不可回滚（只能重建引用）；删除依据是已合并 PR / 等价提交，
  对应提交仍可从 `main` 历史到达或已有归档 ref。
- 未运行完整平台测试：本轮未修改 tracked 源码，运行四项生成契约检查即可；
  若后续要清理工作树/对象包，另立任务并跑相应回归。

## 风险与回滚

- 风险：删除本地分支后，若某个未合并分支被误判为过期，其 tip 在 reflog
  过期前仍可恢复；`attic/` 已保存两处唯一历史。远端分支删除只能重建同名
  引用（提交仍在 GitHub 网络上）。
- 回滚方式：`git branch <name> <sha>` 从 `evidence/local_after.txt` 或
  reflog 恢复；远端用原 SHA push 重建；`attic/*` 分支可直接推送到远端。
- 未触碰用户测试服务的 8787/8792，也未改动 `.work/` 运行资产。

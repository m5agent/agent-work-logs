# PR171 交付与唯一 main 收口

- 日期：`2026-11-05`（Asia/Shanghai）
- 结果：`PASS`（PR171合并、唯一main收口、保全核对和合并后main CI全部完成）
- 工作类型：`code_change`
- 问题来源：用户明确要求完成剩余工作，最终只保留一个main分支。
- 源码版本：[PR171](https://github.com/m5agent/m5stack-esp-emulator/pull/171) 已于 `2026-11-05T07:49:14Z` 合并为 `73ed554fba02a2397dad81e39e12b5b4b92d0500`；与已验收head `ef60f88168b60bc8da685cd007f6658ce0bc0361` 的tree均为 `f01ef76460cffc10f8921e26ec4b82b1ab014060`。
- 环境：Git/GitHub交付、本地历史保全；复用前一执行精确同tree的浏览器virtual-device validation，无新guest。

## 结果

本地活动分支 `26 → 1`，远端仅main。计入本次创建后删除的临时整合分支，共删除26个非main引用：20个main祖先使用安全删除，6个非祖先经离线备份验证后删除。原两个attic无需合并，其历史均已在完整bundle与独立bare仓库保全。

23个旧分支绑定工作树均在原HEAD切为detached。原25个工作树目录完整保留，文件/status、构建/证据/状态资产、旧未跟踪日志及跨工作树依赖链接均未丢失；本次仅移除自建临时整合工作树，未使用force。保留12个tag和1个stash，主检出clean，本地与远端main相同。

PR/push四项CI均成功，合并后四项validator通过；[main CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41989912458)在精确merge SHA上两项job均于终态success。

## 维护设置

启用GitHub合并后自动删除PR分支与本地fetch.prune，默认分支保持main。一个已为main祖先且经过备份验证的旧PR tracking引用也已删除。旧项目服务均正常结束，最终检查未观察到项目监听进程；不公开本机端点。

## 文件

- [report.md](report.md)：完整交付、清理、旧attic判断及边界。
- [run.json](run.json)：结构化结果。
- [delivery-summary.json](evidence/delivery-summary.json)：前后计数及最终身份。
- [final-verification-summary.json](evidence/final-verification-summary.json)：脱敏的逐工作区保全结果。
- [final-deleted-branches-summary.json](evidence/final-deleted-branches-summary.json)：26个删除引用、原SHA与方法。
- [attic-review-summary.json](evidence/attic-review-summary.json)：仅源码/历史REVIEW，无新guest声明。
- [pr171-merge-summary.json](evidence/pr171-merge-summary.json)：合并前四CI终态及真实merge回读。
- [main-ci-summary.json](evidence/main-ci-summary.json)：合并后精确merge SHA的两项CI终态。
- [maintenance-settings-summary.json](evidence/maintenance-settings-summary.json)、[remote-tracking-summary.json](evidence/remote-tracking-summary.json)：维护设置与旧tracking引用清理。
- [phase1-deleted-branches-summary.json](evidence/phase1-deleted-branches-summary.json)：首次24个引用删除的独立快照，保留不覆盖。

## NOT RUN

原25个工作树目录删除、本地资产/cache清空、gc和reflog清理未执行，均不属于本次最终唯一分支目标。没有重复guest、物理硬件或新Pages部署；产品Web/运行时/固件tree未变。本执行不把目录保留解释为未完成分支目标，也不把分支清理解释为新的固件功能验收。

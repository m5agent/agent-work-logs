# PR171 合并与唯一 main 收口：追加执行

本执行追加在[先前固定验证记录](https://github.com/m5agent/agent-work-logs/blob/4fd69c7003c9d05eda3eaa23c296004cc4560a80/records/m5stack-esp-emulator/2026-11-05-repository-branch-tidy/followups/2026-11-05-main-only-closeout/report.md)之后，不回写该快照当时的PR/最终删除pending字段。49项CoreS3 browser-WASM、1986项平台检查（10skip）、30个Node脚本、四项validator、完整历史备份及23工作树原HEAD detach证据保持独立。

## 源码交付

[PR171](https://github.com/m5agent/m5stack-esp-emulator/pull/171) 的head `ef60f88168b60bc8da685cd007f6658ce0bc0361`，base `84b4f4932a402b77c9688aff7b51a1932ff12be6`。PR/push四项CI全部成功后，于 `2026-11-05T07:49:14Z` 真实合并为 `73ed554fba02a2397dad81e39e12b5b4b92d0500`。head与merge的tree均为 `f01ef76460cffc10f8921e26ec4b82b1ab014060`，因此沿用前一执行精确同代码路径的guest证据，不将它表述为又运行了一次merge guest。改动仅两个测试文件、4+/1-，无产品Web、运行时或固件改动。

合并后的四项validator均通过；[main自动CI41989912458](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/41989912458)在精确merge SHA上完成success，network-namespace-policy与platform-contracts两项均成功，最后job于 `2026-11-05T07:53:03Z` 完成。随后最终核对时间为 `2026-11-05T07:53:51.745757+00:00`。

## 删除与历史保全

原26个本地分支最终仅保留main。25个原非main分支加本次临时整合分支，共26个引用被删除；20个已为main祖先，用安全删除；6个非祖先在完整bundle及独立bare对象验证后删除，包含两个旧attic及四个等价topic。最后旧Chrome与临时整合分支均在真实合并后成为main祖先，再安全删除。

完整私有bundle为126,719,820字节，SHA256 `32bae6cc4cdb78b4d3b902a0b590ed859736da8ae513dd2a9b1c2b992a85980f`，独立恢复/fsck/cat-file验证49个引用对象；最终bundle哈希未变。备份二进制不提交。一个旧PR tracking引用也在确认main祖先和备份可读后删除。

## 两个旧attic无需合并

旧local-history含21个独立根历史提交。224个旧文件中216个路径在main存在、115个blob逐字相同；8个旧专有文件是3个固件二进制与5个原始日志，没有旧专有功能source/test/patch路径。七个选定运行时patch中六个逐字相同，C6patch在main扩大；其它测试/工具路径在main保留并扩展。因此没有发现需要合入的独立功能，保全旧内容后删除在线archive引用，不把无关初始根历史混入main。

旧units26只有一个文档计数提交，将133/27调整为139/21，而当前main为158implemented/partial与2planned。它没有可执行改动，合并会恢复陈旧数字。此判断仅为源码与历史REVIEW，不冒充新的guest验收。

## 工作区与运行资产

23个旧分支绑定工作树均在各自原HEAD切为detached；原有一个detached服务工作树也保留。原25个工作树目录全部存在，除主检出按授权更新到merge外，其它HEAD、status与明确保留的本地资产符合预期。两个未跟踪项、旧日志哈希及依赖链接保留；没有删除旧目录。仅移除本次自建临时整合工作树，未使用force。

原12个tag引用和1个stash逐项一致，本地/远端活动heads均仅main，主检出clean。旧项目服务已按授权正常结束，最终只读监听检查未观察到进程；具体端点、进程和路径不复制到公开记录。

## 后续维护

GitHub `delete_branch_on_merge` 从false改为true，本地 `fetch.prune` 从unset改为true，默认分支main不变。这分别帮助清除后续已合并PR head和失效remote tracking引用；不意味着本地开发分支会自动消失。

## 限制与NOT RUN

原工作树目录和本地构建/证据/cache不清空，gc/reflog不清理；分支唯一化不等于抹除历史或运行资产。没有新Pages部署，因产品Web tree未变；没有重复guest、其它板型矩阵、物理硬件、性能比较、长期运行或旧runtime根因闭环的新结论。最初依赖链接与服务观察器解析失败仍保留于前一快照。源码整合、活动分支唯一化、历史与本地资产保全及最终检查均完成；本次范围内没有剩余必需执行项。

# 唯一 main 收口与 Chrome 兼容提交：验证阶段

- 日期：`2026-11-05`（Asia/Shanghai）
- 结果：`PARTIAL`（验证与历史备份通过；源码PR交付与最终分支删除尚未执行；23工作树已原HEAD detach）
- 工作类型：`code_change`
- 问题来源：用户要求完成剩余工作并清理无关分支，后续明确最终只保留一个 `main` 分支。
- 源码版本：`m5agent/m5stack-esp-emulator @ ef60f88168b60bc8da685cd007f6658ce0bc0361`；base `84b4f4932a402b77c9688aff7b51a1932ff12be6`。
- 环境：macOS arm64、Git、GitHub CLI、硬件ANGLE/Metal Chrome；独立 browser-WASM，不使用原生Device Service验证替代。

## 结论

仍有必要的直接脚本Chrome兼容提交已整合为真实双父merge，范围仅两个测试文件、`4+/1-`。实际只设置优先Chrome配置并故意使旧fallback路径无效，CoreS3 stock-reference两代guest完成49项检查，包含真实输入/帧、PIR数据面、暂停/恢复和实际Worker退出。平台1986项（10项skip）、30个Node contract脚本、四项validator及diff/scope检查通过。

完整Git历史已先保存到126,719,820字节的私有bundle，SHA256 `32bae6cc4cdb78b4d3b902a0b590ed859736da8ae513dd2a9b1c2b992a85980f`；独立bare恢复/fsck/cat-file验证49个引用对象，涵盖26个原分支及新增整合分支。备份本体不提交。

23个旧分支绑定工作树已逐个切换为相同HEAD的detached状态，文件、Git status、旧日志哈希和依赖链接保持不变，未删除目录。**当前仍未创建/合并源码PR，未执行最终分支引用删除或目录清理。** 后续交付追加独立execution，不覆盖本次终态与早期失败。

## 关键证据

- 构建或运行：[Chrome guest摘要](evidence/chrome-guest-summary.json)，11,157字节，SHA256 `cc27733d9dfce6e0dd98c49049da8357312fc539c133d7a2fbdb699f1accc815`。
- 产物或部署：[历史备份摘要](evidence/history-backup-summary.json)；仅记录本地Git保全结果，无新Pages部署。
- 实机或服务执行：本次功能结果为 `virtual-device validation`；物理硬件未执行。经授权正常结束两个空闲旧服务进程，与独立浏览器guest结果分开。
- 日志与协议：[完整有界摘要](evidence/summary.json)、[检查及日志哈希](evidence/checks-summary.json)、[23工作树detach摘要](evidence/detachment-summary.json)，保留首次依赖链接和停止前观察器解析失败。

## 文件

- [report.md](report.md)：根因、改动、真实执行与限制。
- [run.json](run.json)：结构化记录。
- `evidence/`：脱敏派生摘要；原报告、备份本体和本机操作日志留在私有本地存储。
- `patches/`：通过精确Git整合提交和base引用源码，不复制二进制产物。
- `code/`：使用源码仓库既有测试入口。

## 未覆盖项

源码PR/合并、最终main远端回读、活动分支唯一化及工作树退役仍 `NOT RUN`。本轮没有产品Web、运行时或固件改动；不新增其它型号、性能、长期稳定性、网络安全或物理硬件结论。

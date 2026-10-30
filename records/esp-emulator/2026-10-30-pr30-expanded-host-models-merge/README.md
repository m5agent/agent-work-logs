# ESP Emulator PR #30 扩展主机模型合并

- 日期：`2026-10-30`
- 结果：`PARTIAL`（代码、CI 与合并 `PASS`；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 问题来源：[PR #30](https://github.com/m5agent/m5stack-esp-emulator/pull/30)
- 源码版本：`m5agent/m5stack-esp-emulator@e3f149c1ffad45ac923e677dea1af599a78c35a6`
- 环境：GitHub Actions、Python 3.12、Node.js 20、Chromium、QEMU WASM

## 结论

PR #30 已与当时的 `main` 完成双父合并，并在修复合并后的视觉运行时和设备
spec 契约后进入 `main`。此前单独的 PR #39 也已完成合并；检查时仓库没有其它
开放 PR。

最终提交通过了平台 `1,658` 项测试、浏览器/preview 契约、离线 Unit 证据测试
和网络隔离测试。PR 自带的虚拟设备证据覆盖新增 Atom/Stick 浏览器准入和
StackChan motion/power 路径；物理硬件未执行。

## 关键证据

- PR #39 合并：`02e6eb1f58f13346a6f4e8059ce401d3336d4c74`。
- PR #30 Git merge commit：`2f95ff23101b0b70f484eb8176a9a4c206a8e866`。
- 合并后契约修复与最终 `main`：`e3f149c1ffad45ac923e677dea1af599a78c35a6`。
- CI：[run 40985661773](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40985661773)。
- 浏览器 runtime lock：`65` 个 patch、`47` 个 native patch、`158` 个
  patched file，完整 replay 成功。
- PR 提供的虚拟设备结果：native peripheral regression `68/68`、`278`
  checks；StackChan browser strict suite `5/5`。
- Pages preview 已部署：
  [站点](https://m5agent.github.io/m5stack-esp-emulator/)、
  [deploy run](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40988933566)。
  线上 runtime 回读为 `20` 个 compiled profiles、`19` 个公开准入设备。
- 静态产物 WASM SHA256：
  `7612dfa18238122f52daea3b40cbf0a3055cb9fe4c6f7b5bc1cfecce7ba5e0dd`。

## 文件

- `report.md`：冲突处理、重编号、验证和边界。
- `run.json`：结构化提交、CI 和验证结果。
- `evidence/summary.json`：可机器读取的合并摘要。

## 未覆盖项

物理 Atom/Stick/StackChan 设备行为、机械运动、供电、射频和电气特性均为
`NOT RUN`。StickC Plus 首次 240 秒 ready timeout 和自然 PWR 清理仍为
`PARTIAL`，没有由合并结果改写为 PASS。

精确 preview artifact 的严格浏览器发布门禁没有通过：GitHub macOS runner
选中了 software WebGL，门禁按设计拒绝继续。页面通过仓库既有的
prepared-preview 路径发布，只用于效果查看，不构成 production browser PASS。

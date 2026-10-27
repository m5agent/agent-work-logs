# ESP Emulator PR #11 合并前审查

- 日期：`2026-10-27`
- 结果：`FAIL`
- 工作类型：`pr_review`
- 问题来源：`https://github.com/m5agent/m5stack-esp-emulator/pull/11`
- 源码版本：`m5stack-esp-emulator @ f2061759897955e6017d4aa2a41bd5ba962c35b6`；PR head `a37342f61c05964c060719a6e35c2d568c828e84`
- 环境：macOS 本地 detached worktree，Python 3.13.15 隔离虚拟环境，Node.js 22.14.0；未使用硬件

## 结论

PR #11 当前不应合并。代码与功能范围很大，但合并门禁首先被仓库体积、公开内容脱敏和可复现 CI 三类问题阻断。平台测试套件实际运行结果为 `1226` 项中 `19 failures + 1 error + 3 skipped`；GitHub 当前没有 PR check，Node 浏览器测试在干净检出中又因未安装 `playwright` 无法启动。未执行完整 UIFlow2 外设矩阵、QEMU 功能回归或物理硬件验证。

## 关键证据

- 变更规模：相对 base 新增 `84,586` 个文件、`26,008,003` 行文本，工作树 blob 总量约 `2.27 GB`；base 约 `27 MB`。
- 证据体积：`docs/evidence/` 新增 `83,096` 个文件，包含 `380` 个 ZIP、`4,280` 张 PNG 和 `10` 个大于 `10 MiB` 的文件。
- 脱敏扫描：新增文件中有 `511` 个包含主机绝对路径，`203` 个包含私网 IPv4 地址；未确认到真实凭据特征。
- 平台门禁：QEMU profiles、peripheral catalog、runtime coverage 与 `compileall` 通过。
- 平台测试：`Ran 1226 tests`，`FAILED (failures=19, errors=1, skipped=3)`。
- 浏览器测试：基础 MJS 检查部分通过，但依赖 `playwright` 的 test bridge 在干净检出中报 `ERR_MODULE_NOT_FOUND`；PR 的 CI workflow 没有执行依赖安装。

## 文件

- [report.md](report.md)：完整审查、复现命令、阻断项和解除条件
- [run.json](run.json)：结构化结果
- [evidence/review-summary.json](evidence/review-summary.json)：变更规模、扫描计数和测试摘要
- `patches/`：不适用，本次仅审查，未修改 PR
- `code/`：不适用，复现命令直接使用 PR 工作树

## 未覆盖项

- 未合并 PR，也未修改或重写贡献者分支。
- 未执行完整 UIFlow2 外设矩阵、QEMU 功能重跑或物理硬件验证。
- 因仓库/GitHub 展示限制，没有逐文件审阅全部 84,586 个新增文件；抽查聚焦核心运行时代码、CI、脱敏规则和关键测试。
- Node 浏览器测试未在补齐依赖后继续作为通过门禁；当前只确认干净检出会因缺失依赖失败。

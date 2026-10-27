# ESP Emulator PR #12 替代合并复评

- 日期：`2026-10-27`
- 结果：`PASS`
- 工作类型：`pr_review`
- 问题来源：`https://github.com/m5agent/m5stack-esp-emulator/pull/12`
- 源码版本：base `f2061759897955e6017d4aa2a41bd5ba962c35b6`；PR head `057ce8b5c3f411b05fcf837e383d45cc6dc95bfc`
- 合并版本：`8a0d99a03e3205564011bb123e0ee981587bebe7`
- 环境：独立远端 clone，Python 3.12.14，Node.js 22.14.0，锁定 Playwright Chromium；未使用硬件

## 结论

PR #12 已解决 #11 的三项合并阻断：源码分支不再包含原始 evidence 大归档，新增内容未发现真实路径/私网端点/凭据泄漏，普通 CI 也不再依赖本机 `.work` 或未安装的 Node 依赖。独立 clone 中平台测试 `1237` 项（`1234` 通过、`3` 跳过）、CI 离线 Unit 契约 `194` 项（`191` 通过、`3` 跳过）、8 个 Node/Chromium 门禁及所有生成检查均通过，因此执行合并。

## 关键证据

- 分支历史：从当前 main 线性增加 3 个提交；独立 clone 中旧 #11 大提交不可达。
- 变更规模：`1,498` 个文件、`206,250` 行新增、`661` 行删除；新增 blob `1,479` 个，共 `111,757,724` bytes，单文件均小于 `10 MiB`。
- evidence：新增 `docs/evidence/` 字节数为 `0`；没有 ZIP、raw trace、pcap、固件/ELF/MAP 或超大归档。
- 脱敏：新增文件中未检出凭据签名；3 个字符串命中均为通过拼接构造的负向测试 fixture，不对应真实主机路径或私网端点。
- 本地独立验证：平台、Node/Chromium、离线 Unit、scope、profiles、catalog、coverage、snapshot 和 compileall 全部通过。
- CI：fork 中同一 head 的 [run 40439239199](https://github.com/yuyun2000/m5stack-esp-emulator/actions/runs/40439239199) 两个 job 均成功；PR 专属 scope step 在 push 事件中跳过，因此使用相同命令在独立 clone 另行执行并确认 `PASS`。
- 合并：PR #12 已合并；合并 commit tree 与已验证的 PR head tree 完全一致。

## 文件

- [report.md](report.md)：复评、复现命令、验证边界和合并结果
- [run.json](run.json)：结构化结果
- [evidence/review-summary.json](evidence/review-summary.json)：体积、脱敏、测试和 CI 摘要
- `patches/`：不适用，本次只复评并合并已有 PR
- `code/`：不适用，使用 PR 自带测试与门禁

## 未覆盖项

- 未重新执行 QEMU/Device Service 功能会话、完整 UIFlow2 外设矩阵或物理硬件验证。
- 新 `0047` runtime 的四主机 FlashLight API/Preview、mounted Web 和完整矩阵仍为 `NOT RUN`；历史结果不继承。
- Node/Chromium 门禁是合成浏览器契约，不等同于完整人工视觉验收或固件数据面 PASS。

# AI Pyramid 文档 llm-llm 下载链接修正与全量 deb 链接审计

- 日期：`2026-10-24`
- 结果：`PASS`（错误路径已定位、替代链接已下载校验、修复 PR 已提交）
- 工作类型：`code_change`
- 问题来源：用户反馈 AI Pyramid 文档中的 `llm-llm` deb 文件链接错误，并要求检查类似问题
- 源码版本：`yuyun2000/m5stack-schematics-text @ 7ae3eab`
- 环境：macOS、curl、Python 3、M5Stack 公共 APT 仓库

## 结论

AI Pyramid 页面声明的 APT 组件是 `jammy ax650c`，但手工下载链接却指向
`jammy/ax630c/v1.9`。由于两个平台都存在同名包且 URL 可正常返回 200，错误不会表现为 404，
而是会下载 LLM630 平台的包。

正确路径（当前 APT 索引最新版）：

```text
https://repo.llm.m5stack.com/m5stack-apt-repo/pool/jammy/ax650c/v1.12/llm-llm_1.12-m5stack1_arm64.deb
```

已验证：HTTP 200、大小 `28,607,168 B`、SHA-256
`8060a5750e6a673b953e6e324854c6c8fccc30d3d4b3c3840fd3007d5e980eae`，与
`dists/jammy/ax650c/binary-arm64/Packages` 中的索引完全一致。

全站 `zh_CN/` 共检查 100 个指向 M5Stack APT 的 `.deb` 链接：无 404，除本例外无其他平台路径
错配；另有 26 个链接仍指向较旧的、可正常下载的版本，属于版本漂移而非坏链，本轮未批量修改。

## 关键证据

- 链接与包索引校验：`evidence/link-verification.txt`
- 100 个链接的逐项结果：`evidence/deb-link-audit.tsv`
- 审计汇总：`evidence/deb-link-audit-summary.txt`
- 最小修复补丁：`patches/0001-fix-ai-pyramid-llm-llm-deb-path.patch`
- 可复现审计脚本：`code/audit_deb_links.py`

## 文件

- `report.md`：根因、修复、验证过程和边界
- PR：https://github.com/yuyun2000/m5stack-schematics-text/pull/2
- `run.json`：结构化记录
- `evidence/`：HTTP/包索引/哈希、全量链接审计与 PR 回读
- `patches/`：可直接应用到 `7ae3eab` 的最小补丁
- `code/`：全量 deb 链接审计脚本

## 未覆盖项

- PR #2 已提交并处于 `OPEN / MERGEABLE`，等待原项目管理员审核；本记录不代表已合并。
- 未批量更新其余 26 个旧版本链接，因为文档可能有意固定特定版本，需逐页确认。

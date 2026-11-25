# M5GFX #445: board_spec product and schematic links for CoreMatrix, Chain Captain and PaperDIY

- 日期：`2026-11-25`
- 结果：`PASS`（无阻塞问题；证据等级 host-level test + live link verification；
  hardware / virtual-device 均 `NOT RUN`，原因是改动不含任何运行时路径）
- 工作类型：`pr-review`
- 条目：[m5stack/M5GFX#445](https://github.com/m5stack/M5GFX/pull/445)，作者 ainyan03，
  英文，OPEN，非 draft；评审前 comments / reviews 均为 0，m5agent 未回复过
- 源码：`m5stack/M5GFX` PR head `f6858acb15fd80a6cc3b7344558b1d0acc9ddc9d`
  （base `develop` tip `5873de4e43b727fab651b71f615246267a816720`，即 merge-base；
  已含 #443 合并）
- 改动范围：5 文件 `+28/-2`，全部在 `extras/board_spec/`
- 环境：macOS 26.5.1 arm64，Node v22.14.0（本机原先无 Node，临时下载官方 arm64 包），
  pypdf 6.21.4；本机 Device Service 36 个 profile 中有 `paperdiy`（partial，ET047TC1
  540x960），无 CoreMatrix / Chain Captain profile

## 结论

无阻塞问题，可按作者方向合入。

- 改动只有三块 `spec.links`（product + schematic + `verified: datasheet`）、一个
  `official_name_verified: true`、由 JSON 重新生成的 editor bundle，以及同步更新的
  catalog 测试名单；不触碰库源码、生成 descriptor 或任何运行时路径。
- 六个链接全部 `200`：三个 docs 页 h1 分别为 `CoreMatrix` / `Chain Captain` /
  `PaperDIY Complete Kit`，页内 SKU 为 C158 / C160 / K159-B，且 PR 里的三个原理图
  PDF 正是这三个页面上挂出的同一 URL（不是猜测或替换）。
- `links.verified.product = datasheet` 与仓库既有约定一致（如 `m5airq`、`m5atoms3`）。
- PaperDIY 保持 `official_name_verified` 不设是对的：页面是 "PaperDIY Complete Kit"；
  仓库内已有 `m5atom_psram` 这种「有 links 但名字未验证」的先例。
- 提交的 `dist/board_spec_editor.html` 确实是生成物：在 head 上重跑 `npm run bundle`
  后工作区无 diff（逐字节一致）。

## 测试基线（PR 与 base 完全同结果）

| 命令 | PR head `f6858ac` | base `5873de4` |
| --- | --- | --- |
| `node cli/spec.js check` | `check passed: 63 board(s), 90 resolved combination(s)` | 同 |
| `npm test` | 221 tests / 220 pass / 1 fail | 221 / 220 / 1 |

唯一失败是 `M5Unified live pin tables match generated values`，属本机环境漂移：作为对照的
M5Unified 检出是 2026-11-06 的旧快照，`compare-pintable` 只报
`m5stampp4xhub in_i2c_scl/sda 1/0 vs 255/255` 两处，与这三个板子无关，且 base 上复现同一失败。
上游 CI 的 `Catalog and generated sources` 为 SUCCESS。

## 文件

- `report.md`：完整报告（改动、逐项核验、测试基线、边界）
- `run.json`：结构化记录
- `evidence/pr445-source.diff`、`pr445-numstat.txt`：源码侧 diff 与统计（bundle 单行过大，
  未整行存入，改用重生成比对）
- `evidence/host-checks.txt`：`spec.js check`、`npm test`（head/base 尾部与失败行）、
  `compare-pintable`、bundle 重生成与 URL 计数
- `evidence/npm-test-pr-head.txt`、`npm-test-develop-base.txt`：两次全量测试原始日志
- `evidence/docs-pages.txt`：六个 URL 的 HTTP 状态、h1、SKU、页面挂出的原理图 PDF
- `evidence/schematic-pdfs.txt`：三份原理图 PDF 的页数/大小/SHA256 与版本串可读性
- `evidence/pr-status.json`、`pr-checks.txt`：PR 状态与 CI 汇总
- `evidence/device-profiles-summary.json`：本机 Device Service profile 实时列表（36 个）

## 未覆盖项

- hardware validation：`NOT RUN`。无 CoreMatrix / Chain Captain / PaperDIY 实机操作；
  且本次改动没有任何固件或设备可观察的行为。
- virtual-device validation：`NOT RUN`。本机有 `paperdiy`（partial）虚拟设备，但
  `extras/board_spec` 的链接元数据不进入固件运行路径，创建会话后也无从观测这次 diff，
  因此未用虚拟设备验证（不是没有 profile 才跳过）。
- 原理图版本号：CoreMatrix 的 `V0.7` 能在图纸文本里读到；Chain Captain 的 `V0.6` 与
  PaperDIY 的 `K159-B` 只由官方 docs 页面上的 PDF 文件名佐证，图纸标题栏为旋转矢量文字，
  本地文本提取读不到，未独立确认。
- 未在真实浏览器里跑 editor 页面渲染（`npm test` 内有链接转义/拒绝可执行 URL 的用例，均通过）。
- 上游 CI 其余项来自 `gh pr checks` 汇总，未在本机逐项复跑；评审时仍有个别 job 为 pending。

## 已发布回复

- 见 `run.json` 的 `posted_comment`。

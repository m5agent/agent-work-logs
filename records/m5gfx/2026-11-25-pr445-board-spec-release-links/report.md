# M5GFX #445 评审报告：board_spec 三个板卡的产品页与原理图链接

## 1. 背景与目标

`m5stack/M5GFX#445`（作者 ainyan03，英文，OPEN）声称 CoreMatrix、Chain Captain、
PaperDIY 三款板卡的官方文档页已公开，于是为 `extras/board_spec` 板卡目录补上
产品页与原理图链接，并顺带把 CoreMatrix 的 `official_name_verified` 置为 true。

目标：只读评审该 PR 是否可以直接合入，不改动上游仓库、不 push、只发一条英文回复。

## 2. 改动范围

base `develop` = `5873de4e43b727fab651b71f615246267a816720`（同时也是 merge-base），
head `f6858acb15fd80a6cc3b7344558b1d0acc9ddc9d`。

| 文件 | +/- | 内容 |
| --- | --- | --- |
| `extras/board_spec/boards/m5stack_corematrix.json` | +9/-0 | `official_name_verified: true` + `spec.links` |
| `extras/board_spec/boards/m5chaincaptain.json` | +8/-0 | `spec.links` |
| `extras/board_spec/boards/m5paperdiy.json` | +8/-0 | `spec.links` |
| `extras/board_spec/dist/board_spec_editor.html` | +1/-1 | 由 JSON 重新生成的 editor bundle |
| `extras/board_spec/test/board_spec.test.js` | +2/-1 | 已验名名单加 `m5stack_corematrix`，未验名名单相应移除 |

没有触碰 `src/`、生成 descriptor、`boards.hpp` 或任何会进入固件的代码。

## 3. 逐项核验

### 3.1 六个链接是否真实存在

- 三个 docs 页与三个 PDF 均 `200`（`evidence/docs-pages.txt`）。
- 三个 PDF 是 `application/pdf`，大小 515 KB / 780 KB / 681 KB。

### 3.2 链接是否就是官方页面上挂出的那一个

抓取三个 docs 页 HTML 后比对页面内的 PDF 链接：PR 中的三个原理图 URL 与页面挂出的
完全一致（CoreMatrix 页面另有 `CoreMatrix_SCH_LED.pdf`，PR 选的是主原理图
`CoreMatrix_V0.7_SCH_PDF_20260609.pdf`，选择合理）。

### 3.3 名称验证前提

- `CoreMatrix` 页面 h1 = `CoreMatrix`，catalog `official_name` = `M5Stack CoreMatrix`，
  符合 schema 中「`M5Stack ` 为目录命名前缀」的说明，置 true 成立。
- `Chain Captain` 页面 h1 = `Chain Captain`。
- `PaperDIY` 页面 h1 = `PaperDIY Complete Kit`，是整套件而非单板，作者保持未验证是对的。
- SKU：页面分别为 C158 / C160 / K159-B，与 PR 描述一致。

### 3.4 约定一致性

- schema：`linkSpec` 允许 `product` / `schematic` / `verified`，
  `verified` 的枚举含 `datasheet`（`schema/board.schema.json:253`、`:52`）。
- 既有先例：`m5airq`、`m5atoms3` 等用 `verified: {product: datasheet, schematic: datasheet}`
  配 docs 页面 URL；`m5atom_psram` 则是「有 links、名字未验证」，与 PaperDIY 的处理同构。

### 3.5 生成的 bundle 是否为真生成物

在 head 上执行 `npm run bundle`，随后 `git status --porcelain .` 为空，说明提交的
`dist/board_spec_editor.html` 与新生成结果逐字节一致，不是手改。六个新 URL 在 bundle 中
各出现 1 次。

### 3.6 测试

| 命令 | PR head | base |
| --- | --- | --- |
| `node cli/spec.js check` | passed: 63 boards / 90 combinations | 同 |
| `npm test` | 221 / 220 pass / 1 fail | 221 / 220 / 1 fail |

唯一失败 `M5Unified live pin tables match generated values` 与本次改动无关：

- 该用例把 catalog 与本地 M5Unified 检出的 `src/M5Unified.inl` 对比；
  本机 M5Unified 是 2026-11-06 快照，已落后于 catalog。
- `compare-pintable` 输出仅两行差异：`m5stampp4xhub in_i2c_scl 1 vs 255`、
  `in_i2c_sda 0 vs 255`，不含这三个板子。
- base 上复跑得到同一失败，证明是环境漂移而非回归。

上游 CI：`Catalog and generated sources` SUCCESS；Arduino 与 ESP-IDF 矩阵多数 SUCCESS，
评审时仍有若干 job 为 pending（不构成本 PR 的阻塞证据）。

## 4. 影响面与风险

- 纯元数据：链接仅供 editor / 目录展示，不参与板卡识别、不进入固件。
- 版本号 `V0.6` / `K159-B` 只由官方 docs 页面文件名佐证；图纸标题栏为旋转矢量文字，
  本地文本提取读不到。对「链接元数据」这一改动级别可以接受，已在回复中如实说明。
- 若日后文档站改版导致 slug 变更，链接会失效；属常规维护成本。

## 5. 结论

`PASS`，无阻塞问题。建议按作者方向合入。

## 6. 执行环境

- macOS 26.5.1 arm64；Node v22.14.0（本机原无 Node，临时下载官方 arm64 二进制包运行仓库
  自带 `cli/spec.js` 与 `npm test`，未改仓库文件）。
- Python 3 + pypdf 6.21.4 用于 PDF 文本抽取。
- 本机 Device Service：`GET /api/v1/devices` 返回 36 个 profile，含 `paperdiy`
  （partial，ET047TC1 540x960，无触摸），无 CoreMatrix / Chain Captain。

## 7. 边界

- hardware validation `NOT RUN`：无相关实物，且改动无可观察的设备行为。
- virtual-device validation `NOT RUN`：有 `paperdiy` profile，但 `extras/board_spec`
  链接元数据不进入运行路径，建会话也无法观测本次 diff。
- 浏览器内 editor 渲染未跑；链接转义/拒绝 `javascript:` 的用例在 `npm test` 内通过。
- 上游 CI 结果取自 GitHub 汇总，未逐项复跑。

## 8. 复现命令

```bash
git fetch origin develop
git fetch origin pull/445/head:pr445
git checkout pr445
cd extras/board_spec
node cli/spec.js check      # check passed: 63 board(s), 90 resolved combination(s)
npm test                    # 221 tests, 220 pass, 1 pre-existing env failure
npm run bundle && git status --porcelain .   # empty => bundle reproducible
```

# M5GFX #437: 把 arduino-esp32 3.3.13 / 4.0.0 加进 Arduino CI 矩阵（CI 构建级验证）

- 日期：`2026-11-20`
- 结果：`PASS`（host-level CI 构建；改动只涉及 Actions 矩阵，硬件/虚拟设备不适用）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#437](https://github.com/m5stack/M5GFX/pull/437)
  「CI: build the latest arduino-esp32 3.3 and 4.0 releases」，作者 ainyan03，英文，OPEN
- 源码：PR head `6be660c181c860a89acc978320f765f03ff5433c`，base `develop`
  `44324f34748812ce557e0dea39fb173cf9a73952`
- 环境：GitHub Actions `ubuntu-latest` + `arduino-cli 1.1.1`（PR 自带 CI，run 44725782321）；
  macOS arm64 本机只做只读取证与源码/元数据比对，未做本地独立重建

## 结论

1. 改动只有 `.github/workflows/ArduinoBuild.yml` 一个文件，`+43/-2`。矩阵从 11 行变 21 行，
   新增的正好是 10 行（3.3.13 与 4.0.0 各 5 行：esp32 / s3 / c5 / p4，以及另一颗 P4 芯片
   版本的 `ChipVariant` 行），没有删除任何旧行，也没有出现重复的 (board, version) 组合。
2. 版本事实成立：Espressif 板管理器索引当前最新为 `4.0.0`，其次 `3.3.13`；官方 release 标题
   分别是「based on ESP-IDF v6.1.1」与「based on ESP-IDF v5.5.6+」，与 PR 正文一致。
3. P4 芯片版本的说法成立，且两条 P4 行不是重复构建：3.3.13 的 `esp32p4.build.chip_variant`
   默认是 `esp32p4_es`（rev < 3），4.0.0 默认是 `esp32p4`（rev ≥ 3）；两个 tag 的
   `menu.ChipVariant` 都提供 `prev3` / `postv3`，PR 用的 FQBN 选项合法。`platform.txt` 用
   `{build.chip_variant}` 选择预编译 SDK 目录，所以 `postv3` 行实际链的是 `esp32p4` 库、
   默认行链的是 `esp32p4_es` 库；产物大小也不同（3.3.13：450064 vs 451408 字节；
   4.0.0：465474 vs 468436 字节），证明确实编了两颗芯片版本。
4. head 上 Arduino Build 21/21 作业成功，其中 10 个新作业 69–107 s 全部 success；该 commit 上
   全部 38 项检查 success，PR 为 MERGEABLE/clean。
5. 矩阵顶部注释关于「哪些 release 只由一侧 CI 构建」的描述与两侧工作流一致：M5Unified CI
   （develop）覆盖 3.0.7 / 3.2.1 / 3.3.12 + M5Stack 包，并且克隆 M5GFX 时按 base 分支
   （master 否则 develop）取代码，所以 M5GFX 的 PR 确实不会在 3.0 / 3.2 上被构建。
6. 无阻塞问题。一条非阻塞提醒：新注释里「latest release of each current series 由两侧 CI
   共同构建」只有在 M5Unified 侧同形 PR #445（3.3.12→3.3.13，并新增 4.0.0）一并合入后才成立；
   在该 PR 合入前 M5Unified 仍停在 3.3.12，建议两个 PR 同批合入，或先合 M5Unified 侧。

## 关键证据

- `evidence/ci-jobs.txt`：head `6be660c` 的 Arduino Build 21 个作业结论与起止时间、
  38/38 检查通过、四个 P4 作业的 sketch 体积（证明 `ChipVariant` 生效）。
- `evidence/version-metadata.txt`：板管理器索引前 5 个版本、两个 release 的 IDF 版本与发布时间、
  两个 tag 的 `boards.txt` esp32p4 默认值与 `menu.ChipVariant` 原文、`platform.txt` 的
  `compiler.sdk.path` / `build.chip_variant` / `-DF_CPU` 行。
- `evidence/diff-scope.txt`：base/head、`+43/-2`、11→21 行、新增 10 行清单、M5Unified
  CI 矩阵与克隆分支逻辑、M5Unified 同形 PR #445 的元数据。
- `patches/0001-ci-arduino-latest.patch`：PR head 的差分，已在 base `44324f3` 上
  `git apply --check` 通过。
- 已发布回复：见 PR #437 下 m5agent 的唯一一条英文评论（本记录归档后发布，链接在后续提交中回填）
  （PR 仍 OPEN，未 close、未 push 上游、未改他人代码）

## 未覆盖项

- 本地独立重建：`NOT RUN`。本机未安装 arduino-cli，也没有下载 3.3.13 / 4.0.0 平台包，
  因此没有在 PR CI 之外独立编译；结论依赖上游 Actions 的执行结果与所引用的公共元数据，
  两者都已在 evidence 中留原文。
- hardware validation：不适用。改动只增加 CI 构建行，不改变任何运行时行为。
- virtual-device validation：不适用，且是结构性的：矩阵变化不产生新的固件行为，任何模拟设备
  上都不可能观察到差异；唯一可观测量是「构建是否成功」，已由 CI 覆盖。
- P4 硅片上的实际运行（rev < 3 与 rev ≥ 3 的板子）：`NOT RUN`。本 PR 只承诺「能编过」，
  不代表两颗芯片版本都在真实硬件上启动过。

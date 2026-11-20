# M5Unified #445: 在 Arduino CI 中加入 arduino-esp32 3.3.13 / 4.0.0（CI 构建级验证）

- 日期：`2026-11-20`
- 结果：`PASS`（host-level CI 构建；改动只涉及 Actions 矩阵，硬件/虚拟设备不适用）
- 工作类型：`pr`
- 条目：[m5stack/M5Unified#445](https://github.com/m5stack/M5Unified/pull/445)
  「CI: build the latest arduino-esp32 3.3 and 4.0 releases」，作者 ainyan03，英文，OPEN
- 源码：PR head `3d7abeed4cdf46f3791fa61ae30618d4f700ba67`（单提交），base `develop`
  `6df015290976764e5e71beffe28abcd25dc54818`
- 环境：GitHub Actions `ubuntu-latest` + `arduino-cli 1.1.1`（PR 自带 CI，run 44725789948；
  作者 fork 同 head run 44696180242）；macOS arm64 本机只做只读取证与公共元数据比对，
  未做本地独立重建

## 结论

1. 改动只有 `.github/workflows/ArduinoBuild.yml` 一个文件，`+35/-7`。矩阵从 15 行变 21 行：
   4 行由 3.3.12 改名为 3.3.13（esp32 / s3 / c5 / p4），新增 3.3.13 的 P4 `postv3` 行，
   新增 4.0.0 的 5 行（esp32 / s3 / c5 / p4 与 P4 `prev3`）。没有删除旧 job，也没有出现
   重复的 (board, version, variant) 组合；patch 在 base `6df0152` 上 `git apply --check` 通过。
2. 版本事实成立：Espressif 板管理器索引当前最新为 `4.0.0`，其次 `3.3.13`；官方 release 标题
   分别是「based on ESP-IDF v6.1.1」（2026-11-19）与「based on ESP-IDF v5.5.6+」（2026-11-17），
   与 PR 正文一致。
3. P4 芯片版本的说法成立，两条 P4 行不是重复构建：3.3.13 的 `esp32p4.build.chip_variant`
   默认 `esp32p4_es`（rev < 3），4.0.0 默认 `esp32p4`（rev ≥ 3）；两个 tag 都提供
   `menu.ChipVariant.prev3` / `postv3`，PR 用的 FQBN 选项合法。`platform.txt` 的
   `compiler.sdk.path` 使用 `{build.chip_variant}` 选预编译 SDK，因此 `postv3` 行链
   `esp32p4` 库、默认行链 `esp32p4_es` 库；CI 产物大小也不同（3.3.13：538300 默认 vs
   539696 `postv3`；4.0.0：531556 默认 vs 534536 `prev3`），说明确实编了两颗芯片版本。
4. head 上 Arduino Build 21/21 作业成功，10 个新增/改名行全部 success（69–115 s），
   该 commit 37/37 检查通过，PR 为 `MERGEABLE` / `CLEAN`；作者 fork 的同一 head 也是 21/21。
5. 矩阵顶部注释关于两侧 CI 分工的描述与现状一致：M5Unified CI 覆盖 3.0.7 / 3.2.1 / 3.3.13
   + M5Stack 包，克隆 M5GFX 时按 base 分支（master 否则 develop）取代码；M5GFX CI 覆盖
   2.0.17 / 3.1.3 / 3.3.0(C5) / M5Stack 2.1.4，且不构建 M5Unified，所以 M5GFX 的 PR
   确实不会在 3.0 / 3.2 上被构建。
6. 无阻塞问题。两条非阻塞提醒：(a) 同形 PR [m5stack/M5GFX#437](https://github.com/m5stack/M5GFX/pull/437)
   目前仍 OPEN，「latest release built by both CIs」这句话要两侧都合入后才完全成立；
   (b) 4.0.0 行只覆盖 esp32 / s3 / c5 / p4，C3 / C6 / H2 在 4.0 上仍不构建（与既有 3.3
   行的覆盖形状一致），这三款 SoC 的 4.0 专有回归不会被这套矩阵发现。

## 关键证据

- `evidence/ci-jobs.txt`：head `3d7abeed` 的 Arduino Build 21 个作业结论与起止时间、
  10 个新增/改名行的逐行结果、作者 fork 21/21、37/37 检查、ESP-IDF Build 14/14。
- `evidence/new-matrix-rows-builds.txt`：10 个新增/改名行的实际 platform 版本（3.3.13 / 4.0.0）、
  sketch 体积、`error:`/`warning:` 计数；两条 P4 `ChipVariant` 作业的编译命令与
  `Used platform` 原文；构建目标是 `examples/Test/build_test`（调用 M5Unified API 的
  compile-only 示例）。
- `evidence/arduino-esp32-versions.txt`：板管理器索引版本列表、两个 release 的 IDF 版本与
  发布时间、两个 tag 的 `boards.txt` esp32p4 默认值 / `menu.ChipVariant` 原文、
  `platform.txt` 的 `compiler.sdk.path` 与 `build.chip_variant` 行。
- `evidence/matrix-and-split.txt`：M5GFX develop 与 M5Unified head 的矩阵逐行清单、
  工作流里的 M5GFX 克隆与 FQBN 编译行、M5GFX #437 的同形新增行。
- `evidence/diff-scope.txt`：base/head、`+35/-7`、15→21 行、job 名唯一性、
  `git apply --check` 结果；`patches/0001-ci-arduino-latest.patch` 为 PR head 差分。
- 已发布回复：<https://github.com/m5stack/M5Unified/pull/445#issuecomment-7038352238>
  （1 条，英文；PR 仍 OPEN，未 close、未 push 上游、未改他人代码）
- 同批对照：`records/m5gfx/2026-11-20-pr437-arduino-latest-ci/`（另一侧同形 PR 的评审记录）。

## 未覆盖项

- 本地独立重建：`NOT RUN`。本机未安装 arduino-cli，也没有下载 3.3.13 / 4.0.0 平台包，
  因此没有在 PR CI 之外独立编译；结论依赖上游 Actions 的执行结果与所引用的公共元数据，
  两者都已在 evidence 中留下原文。
- hardware validation：不适用。改动只增加 CI 构建行，不改变任何运行时行为。
- virtual-device validation：不适用，且是结构性的：矩阵变化不产生新的固件行为，任何模拟设备
  上都不可能观察到差异；唯一可观测量是「构建是否成功」，已由 CI 覆盖。
- 运行期验证：`NOT RUN`。CI 只编译 `examples/Test/build_test`，没有烧录、启动或外设行为；
  4.0.0（ESP-IDF 6.1.1）下的实际显示 / 触摸 / 联网行为不在本 PR 的承诺范围内。
- P4 硅片上的实际运行（rev < 3 与 rev ≥ 3 的板子）：`NOT RUN`，本 PR 只证明两颗芯片版本
  都能编过。

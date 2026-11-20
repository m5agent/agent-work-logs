# M5Unified #445 评审报告：Arduino CI 加入 arduino-esp32 3.3.13 / 4.0.0

## 1. 背景与目标

arduino-esp32 4.0.0（ESP-IDF 6.1.1）与 3.3.13（ESP-IDF 5.5.6+）先后成为当前两条系列的最新
release，但 M5Unified 的 Arduino CI 还停在 3.3.12，4.0.0 完全没有构建。M5GFX 与 M5Unified
两侧的 CI 一直用「分工」的方式覆盖 2.0–3.3 的各个系列：每个系列只由一侧构建；而一个 PR 只跑
自己仓库的 CI，所以「只由另一侧 CI 构建的 release」永远不会检查本仓库的 PR。作者的处理是：
最新 release（3.3.13、4.0.0）两侧都构建，旧 release 继续分工，并在同一 PR 系列里对 M5GFX
做同样改动（[M5GFX#437](https://github.com/m5stack/M5GFX/pull/437)）。

评审要回答四件事：

1. 改动是否只有 CI 矩阵，新增行是否真的被执行、是否通过；
2. 3.3.13 / 4.0.0 的版本事实是否成立；
3. P4 `ChipVariant` 两行是否真的指向不同的芯片版本，而不是重复构建；
4. 矩阵顶部新注释对两侧 CI 分工的描述是否与现状一致。

## 2. 改动范围

`.github/workflows/ArduinoBuild.yml`，`+35/-7`，只改矩阵与注释：

| 变化 | 行 |
| --- | --- |
| 3.3.12 → 3.3.13 改名 | esp32 / esp32s3 / esp32c5 / esp32p4（4 行） |
| 新增 3.3.13 | esp32p4 `ChipVariant=postv3`（1 行） |
| 新增 4.0.0 | esp32 / esp32s3 / esp32c5 / esp32p4 / esp32p4 `ChipVariant=prev3`（5 行） |

- base `6df0152`（develop），head `3d7abeed`，单提交；矩阵 15 → 21 行，job 名无重复。
- `patches/0001-ci-arduino-latest.patch` 在 base 上 `git apply --check` 通过；把 patch 应用到
  base 后与 API 取回的 head 工作流逐字节相同（`diff -u` 为空），说明评审用的文件就是 head。
- 没有源码、示例、库或 API 改动。

## 3. 方法

改动只影响「构建哪些配置」，没有任何运行时行为路径，因此不选择实机或模拟设备：任何能编过的
配置产生的库代码与 base 相同，唯一观测量是构建成功/失败。取证分两层：

### 3.1 host-level：读 PR head 的真实 CI 执行结果

- 上游 `m5stack/M5Unified` Arduino Build run 44725789948（`pull_request`，head `3d7abeed`），
  逐 job 读取结论、起止时间，并对 10 个新增/改名 job 拉完整日志，提取实际使用的 platform
  版本、`Used platform`、sketch 体积与 `error:` / `warning:` 计数。
- 作者 fork 的同 head run 44696180242 作为第二份执行记录。
- 同一 commit 上的其它工作流（SourceCheck、Forward events、ESP-IDF Build）单独记录，避免把
  与本 PR 无关的作业状态混进结论。

### 3.2 code-level：公共版本元数据与板卡定义

- 板管理器索引 `package_esp32_index.json`：确认 `4.0.0`、`3.3.13` 存在且为各自最新。
- 官方 release：确认 4.0.0 = ESP-IDF v6.1.1、3.3.13 = ESP-IDF v5.5.6+ 及发布时间。
- 两个 tag 的 `boards.txt`：确认 `esp32p4` 的默认 `chip_variant` 与 `menu.ChipVariant`
  选项；两个 tag 的 `platform.txt`：确认 `compiler.sdk.path` 用 `{build.chip_variant}`
  选择预编译 SDK 目录。
- 两侧仓库当前 `ArduinoBuild.yml` 的矩阵逐行对比，以及 M5Unified 里克隆 M5GFX 的分支逻辑。

## 4. 观察

### 4.1 CI 结果

| 工作流 | 结果 |
| --- | --- |
| Arduino Build（上游，run 44725789948） | 21/21 success，整轮约 6 分钟 |
| 其中 10 个新增/改名 job | 全部 success，单个 69–115 s |
| 作者 fork Arduino Build（run 44696180242） | 21/21 success |
| ESP-IDF Build（run 44725790078，未被本 PR 修改） | 14/14 success |
| PR 全部检查 | 37/37 pass，`MERGEABLE` / `CLEAN` |

10 个新增/改名 job 的日志都显示实际使用的 platform 与 job 名一致（3.3.13 或 4.0.0），
`error:` / `warning:` 计数为 0：

| job | platform | sketch 字节（占比） |
| --- | --- | --- |
| esp32 (3.3.13) | 3.3.13 | 529754（40%） |
| esp32s3 (3.3.13) | 3.3.13 | 553363（42%） |
| esp32c5 (3.3.13) | 3.3.13 | 525712（40%） |
| esp32p4 (3.3.13) | 3.3.13 | 538300（41%） |
| esp32p4:ChipVariant=postv3 (3.3.13) | 3.3.13 | 539696（41%） |
| esp32 (4.0.0) | 4.0.0 | 536839（40%） |
| esp32s3 (4.0.0) | 4.0.0 | 565159（43%） |
| esp32c5 (4.0.0) | 4.0.0 | 529882（40%） |
| esp32p4 (4.0.0) | 4.0.0 | 531556（40%） |
| esp32p4:ChipVariant=prev3 (4.0.0) | 4.0.0 | 534536（40%） |

### 4.2 版本事实

- 索引最新 8 个版本：`4.0.0, 3.3.13, 3.3.12, 3.3.11, …`，`4.0.0` 为最新，`3.3.13` 为最新 3.3。
- 4.0.0 release 标题：`ESP32 Arduino Release 4.0.0 based on ESP-IDF v6.1.1`，发布
  2026-11-19T01:45Z；3.3.13：`based on ESP-IDF v5.5.6+`，发布 2026-11-17T16:34Z。
- PR 正文「4.0.0 (ESP-IDF 6.1.1)」「3.3.13 是 3.3 最新」两处均与公开事实一致。

### 4.3 P4 两颗芯片版本

| release | `esp32p4.build.chip_variant` 默认 | `menu.ChipVariant` |
| --- | --- | --- |
| 3.3.13 | `esp32p4_es`（rev < 3） | `prev3` → `esp32p4_es`；`postv3` → `esp32p4` |
| 4.0.0 | `esp32p4`（rev ≥ 3） | `prev3` → `esp32p4_es`；`postv3` → `esp32p4` |

- `platform.txt`（两个 tag）都有
  `compiler.sdk.path={tools.esp32-arduino-libs.path}/{build.chip_variant}`，所以 FQBN 的
  `ChipVariant` 真正切换预编译 SDK 目录，不是同一个目标换名字。
- 产物大小随之不同：3.3.13 默认 538300 vs `postv3` 539696；4.0.0 默认 531556 vs `prev3`
  534536。这说明每个 release 的两条 P4 行确实编了两颗芯片版本。
- PR 正文「3.3 默认 pre-v3、4.0 默认 rev3+，每个 release 另编另一颗」的说法成立。

### 4.4 两侧 CI 分工与新注释

| 仓库 / 分支 | 矩阵覆盖 |
| --- | --- |
| M5GFX @ develop | 2.0.17（esp32/s3/c3）、3.1.3（esp32/s3/c3/c6/p4/h2）、3.3.0（c5）、M5Stack 2.1.4 |
| M5Unified @ head | 3.0.7（esp32/s3/c3/c6/h2）、3.2.1（esp32/s3/c6/p4）、3.3.13（esp32/s3/c5/p4+postv3）、4.0.0（同前四款+prev3）、M5Stack 3.2.5/3.2.5 |

- 与注释一致：2.0 / 3.1 只在 M5GFX，3.0 / 3.2 只在 M5Unified，3.3 的 C5 最早版本只在 M5GFX。
- M5Unified 的工作流按 base 分支（master 否则 develop）克隆 M5GFX，构建时编的是 M5GFX 该
  分支的代码；M5GFX 的 CI 没有任何构建 M5Unified 的步骤。因此「M5GFX 的 PR 不会在 3.0 / 3.2
  上被构建」成立。
- 同形 PR M5GFX#437（OPEN）新增的行与本 PR 一致（3.3.13 / 4.0.0 各 5 行，含两条 P4
  `ChipVariant`），两侧配对没有问题。

### 4.5 构建目标

`examples/Test/build_test/build_test.ino` 只 `#include "main/main.cpp"`；`main.cpp` 包含
`<M5Unified.h>`，并调用 `M5.Display` / `M5.Speaker` / `M5.Mic` / `M5.Imu` / `M5.Touch` /
`M5.Btn*` 等 API。也就是说 CI 编译的是 M5Unified 的真实 API 面，但只到「能链接成 BIN」为止：
没有烧录、启动、外设或网络行为。

## 5. 结论与非阻塞项

无阻塞问题，同意按当前形状合入。两条非阻塞提醒：

1. 「latest release 由两侧 CI 共同构建」只有在 M5GFX#437 一并合入后才完全成立；建议两个 PR
   同批合入，避免其中一侧的注释短暂领先于现实。
2. 4.0.0 行只覆盖 esp32 / s3 / c5 / p4；C3 / C6 / H2 在 4.0 上仍不构建（与既有 3.3 行的覆盖
   形状相同）。如果 4.0 对这几款 SoC 有专有回归，这套矩阵不会发现。是否补行属于覆盖成本
   取舍，不影响本 PR 的正确性。

## 6. 未覆盖、风险与回滚

- 未做本地独立重建（`NOT RUN`）：本机没有 arduino-cli 与 3.3.13 / 4.0.0 平台包；本 PR 的
  可验证对象本身就是 YAML 矩阵，PR 自带 CI 已按该矩阵真实执行，手工 `arduino-cli` 重建反而
  不会执行 YAML 变更。
- 运行期 / hardware / virtual-device：均不适用（结构性）。构建成功不等于 4.0.0 下显示、触摸、
  音频、联网行为正确；这些不在 CI PR 的承诺范围内，本次未验证。
- P4 两种芯片版本的真实硅片启动：`NOT RUN`。
- 风险与回滚：改动只增加/改名 CI 行，最坏影响是 CI 时长与偶发构建失败；回滚即恢复
  `ArduinoBuild.yml` 到 base `6df0152`，不涉及库代码或发布物。

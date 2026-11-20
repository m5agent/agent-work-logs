# 报告：M5GFX #437 CI 矩阵新增 arduino-esp32 3.3.13 / 4.0.0

## 任务背景

`m5stack/M5GFX#437`（作者 ainyan03，英文，2026-11-20 创建）为 Arduino CI 矩阵新增
arduino-esp32 `3.3.13`（最新 3.3）与 `4.0.0`（最新，ESP-IDF 6.1.1）两批构建行，理由是：

1. M5GFX 与 M5Unified 的 Arduino CI 一直把旧 release 拆开跑，而一个 PR 只跑自己仓库的 CI，
   M5GFX CI 又不构建 M5Unified，所以「只被另一个 CI 覆盖的 release」对 M5GFX 的 PR 是盲区；
2. 用户最常装的是各系列的最新版，因此把 3.3 / 4.0 的最新版同时加到两侧 CI；
3. esp32p4 在 3.3 与 4.0 上默认芯片版本不同（3.3 默认 rev < 3，4.0 默认 rev ≥ 3），
   因此每个 release 额外构建另一颗芯片版本。

任务目标是只读复验该 PR 的事实与 CI 结果，按条目语言（英文）发一条评论，不关闭、不 push 上游。

## 基线

- base：`develop` @ `44324f34748812ce557e0dea39fb173cf9a73952`
- head：`6be660c181c860a89acc978320f765f03ff5433c`（单 commit，1 文件，`+43/-2`）
- 改动前矩阵 11 行，改动后 21 行；新增 10 行、删除 0 行；无重复的 (board, version) 组合。
- 首次取数时 PR 0 条评论、0 条 review，m5agent 未回复过。

## 验证过程与证据

### 1. 版本事实（公共元数据）

- `package_esp32_index.json` 的平台版本顺序为 `4.0.0, 3.3.13, 3.3.12, ...`，即 4.0.0 与
  3.3.13 分别是当前最新与最新 3.3，PR 标题与正文的前提成立。
- 官方 release 标题：`4.0.0` → "based on ESP-IDF v6.1.1"（2026-11-19 发布）；
  `3.3.13` → "based on ESP-IDF v5.5.6+"（2026-11-17 发布）。PR 正文写的 `4.0.0 (ESP-IDF 6.1.1)`
  准确。

### 2. P4 芯片版本与 FQBN 选项

- `boards.txt`（tag `3.3.13`）：`esp32p4.build.chip_variant=esp32p4_es`（默认 rev < 3），
  `menu.ChipVariant.prev3` → `esp32p4_es` / 360 MHz，`postv3` → `esp32p4` / 400 MHz。
- `boards.txt`（tag `4.0.0`）：`esp32p4.build.chip_variant=esp32p4`（默认 rev ≥ 3），
  菜单项相同但 `postv3` 排在前面、`prev3` 在后。
  结论：PR 的「3.3 默认 pre-v3、4.0 默认 v3+，各自再补另一颗」描述与官方 boards.txt 一致，
  `ChipVariant=postv3` / `prev3` 两个取值在两个 tag 中都存在。
- `platform.txt` 中 `compiler.sdk.path={tools.esp32-arduino-libs.path}/{build.chip_variant}`，
  即菜单选择会切换预编译 SDK 目录；同时 `-DF_CPU={build.f_cpu}` 随选项变化。
- CI 实测（Arduino Build run 44725782321）四个 P4 作业的 sketch 体积互不相同：
  3.3.13 默认 450064 字节 vs `postv3` 451408 字节；4.0.0 默认 465474 字节 vs `prev3`
  468436 字节。若 `ChipVariant` 未生效，同 release 的两行应产出同一体积。由此可判定两条
  P4 行确实分别构建了不同芯片版本，不是重复作业。

### 3. CI 执行结果

- head `6be660c` 上 Arduino Build：21/21 作业 `success`。10 个新作业耗时 69–107 s：
  3.3.13 的 esp32/s3/c5/p4/p4-postv3 与 4.0.0 的 esp32/s3/c5/p4/p4-prev3 全部成功。
- 该 commit 全部 38 项检查 `success`（含 ESP-IDF 系列构建与 translation unit consistency）。
- PR `MERGEABLE` / `mergeable_state=clean`。

### 4. 与 M5Unified 的拆分描述是否准确

- M5Unified `develop` 的 `ArduinoBuild.yml` 覆盖 3.0.7 / 3.2.1 / 3.3.12 与 M5Stack 包
  （3.2.5，core + cores3），因此 3.0 / 3.2 系列只有 M5Unified 构建、2.0 / 2.1 / 3.1 只有
  M5GFX 构建，与 PR 新注释一致。
- M5Unified CI 取 M5GFX 的方式是 `git clone --depth 1 --branch "$BRANCH"`，其中
  `BRANCH="${base_ref:-ref_name}"` 且非 master 时归一到 `develop`，所以 M5GFX 的 PR
  确实不会在 3.0 / 3.2 上被构建，这也是本次「最新版两侧都建」的理由。
- M5Unified 侧存在同形 PR #445（open，`+35/-7`，同样 1 个文件）：把 3.3.12 行改为 3.3.13，
  并新增 4.0.0 的 5 行。这一点构成一条非阻塞提醒：只有 #445 一并合入后，M5GFX 注释里
  「latest release of each current series is built by both CIs」才成立；否则 M5Unified 侧
  仍停在 3.3.12。

## 结论

- 改动范围单一、事实核对全部通过、CI 全绿，可以作为 CI 覆盖补强合入，无阻塞问题。
- 唯一非阻塞项是跨仓库合入顺序（与 M5Unified #445 同批），不影响本 PR 自身正确性。

## 未覆盖项与风险

- 本地独立重建 `NOT RUN`：本机未安装 arduino-cli，未下载 3.3.13 / 4.0.0 平台包；结论依赖
  上游 Actions 运行结果 + 公共元数据原文，二者均已留证。
- hardware validation：不适用（只改 CI 矩阵，无运行时行为变化）。
- virtual-device validation：结构性不适用；矩阵变化不产生固件行为差异，模拟设备无可观测量。
- P4 两颗芯片版本在真实硅片上的启动：`NOT RUN`，本 PR 只承诺可编译。
- 回滚方式：revert 该 commit 即恢复 11 行矩阵；无数据/接口影响。

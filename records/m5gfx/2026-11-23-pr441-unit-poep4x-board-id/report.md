# M5GFX #441 评审报告：Add Unit PoEP4X board id.

## 背景

- 条目：m5stack/M5GFX#441，作者 TinyuZhao，2026-11-23 08:00Z 创建，OPEN，正文为空。
- 目标：为新板卡保留一个 `board_t` 枚举值，便于后续 M5Unified / 检测代码引用。
- 评审范围：只读核对 diff、ID 空间、命名、引用面与 fixed-board 行为；不改上游仓库。

## 改动

```
src/lgfx/boards.hpp
@@ -84,6 +84,7 @@
     , board_M5StampP4X = 156
     , board_M5StampP4XHub = 157
     , board_M5StamP4XHub = board_M5StampP4XHub // same board, alternate spelling
+    , board_M5UnitPoEP4X = 158
```

1 file，+1 行，无其他改动。

## 核对结果

### 1. ID 空间

`boards.hpp` 在 PR head 的分段：

- 显示类板卡：1..35（含 `board_M5Tab5X = 35`）。
- 非显示板卡：128..157（`board_M5StampP4XHub = 157` 为当前最大值）。
- 外部显示：192..201（`board_M5AtomDisplay = 192` 起）。
- `board_FrameBuffer = 512`。

158 是 157 之后的下一个值，仍小于 192，落在非显示区间；不与 148（`board_M5UnitPoEP4`）、
157、201（`board_M5UnitPoEP4DisplayOut`）等既有值重复。

用最小 TU + `static_assert` 在 host 编译验证（`evidence/board_id_check.cpp`）：

- `static_cast<std::uint32_t>(board_M5UnitPoEP4X) == 158`
- 不等于 148 / 157 / 201
- 小于 `board_M5AtomDisplay`（192）

`g++ -std=c++17 -Wall -Wextra -Werror -I src -fsyntax-only` exit 0。

### 2. 命名与位置

- 同族参照：`board_M5UnitPoEP4`（148）→ 新名 `board_M5UnitPoEP4X`，只加 `X` 后缀。
- 同后缀参照：`board_M5StampP4`（150）→ `board_M5StampP4X`（156）。
- 位置紧接 157 的拼写别名之后，仍在 `/// external displays` 分界之前；符合该文件按
  产品族/分段追加的写法。

### 3. 引用面与运行时行为

在 PR head 全树 `git grep board_M5UnitPoEP4X` 只命中 `src/lgfx/boards.hpp:87` 自身：

- 没有 `esp32p4_boards[]` 条目；
- 没有 SDL 标题映射（`src/M5GFX.cpp:1140-1157`，未命中时走 `default: "M5GFX"`）；
- 没有 fixture / 生成表条目。

因此本 PR 不改变任何既有代码路径，也不会改变现有板卡的检测结果。代价是该 ID 目前
不可通过 fixed board 选中：

- `select_fixed_board()` 在 `esp32p4_boards[]` 中按 ID 查找，找不到返回 `nullptr`
  （`src/board_detect/detection_package.inl:65-86`）。
- `M5GFX::init_impl()` 在 `entry == nullptr` 时打印
  `Fixed board:%u is not supported by this chip` 并返回 false（`src/M5GFX.cpp:910-929`）。

这与 `esp32p4.inl:412` 对 `board_M5StampP4` 的说明一致（“No detector: selectable only
through fixed_board”），也说明“先留 ID、后补 descriptor/detector”在本仓库是既有节奏。

### 4. 先例

同作者此前两次同类提交均为单行预留，且均先合并、后补命名/检测：

- `f4923a7`（2026-01-22）“Add Unit PoEP4 board id.”：只加 `board_M5UnitPoEP4` 一行，
  `src/lgfx/boards.hpp` +1；后续才出现 148 的 descriptor 与 fixture。
- `8d036e1`（2026-11-04）“Add new board ID for M5StampP4XHub.”：只加
  `board_M5StamP4XHub = 157` 一行；次日 `dc21d40` 由 maintainer 更名为
  `board_M5StampP4XHub` 并保留旧拼写别名。

本次 PR 的形态与上述两次一致；没有证据表明项目要求 ID 预留必须同时带 detector。

### 5. CI

PR head `bb02d2e` 的上游 GitHub Actions：39/39 SUCCESS，包含：

- `Board detection host tests` / job `host`：SUCCESS
- `SourceCheck` / `translation unit consistency`：SUCCESS
- Arduino（2.0.17 / 3.1.3 / 3.3.0 / 3.3.13 / 4.0.0、m5stack_core 2.1.4）与 ESP-IDF
  （5.1.6 / 5.4.3 / 5.5.2 / 6.0.2）多目标构建：SUCCESS

仅表示编译与既有 host 测试通过，不代表运行或硬件验证。

## 影响面与兼容性

- 对现有板卡：无影响，新增枚举未被任何代码引用。
- 对下游：第三方若自行使用数值 158，现被 M5GFX 正式占用；由于此前 158 未分配，
  这是预期的 ID 预留行为。
- ABI：仅新增枚举常量，不改变既有值；`board_t` 底层类型与既有序列不变。
- 回滚：删除该行即可，无状态迁移。

## 未覆盖项与风险

- hardware validation：`NOT RUN`，无 Unit PoE-P4X 实物。
- virtual-device validation：`NOT RUN`，见 `evidence/environment.txt`；改动无运行时路径，
  且本机无对应 profile/模型。
- 产品名与 ID 的最终对应关系：只按 PR 标题与既有命名推断，未从公开产品页核实
  （未找到公开的 PoE-P4X 资料，不将其作为结论依据）。
- 后续 detector / 生成表 / 文档同步不在本 PR 范围，未验证。

## 结论

无阻塞项。ID 取值、位置、命名与预留方式均符合仓库既有做法，CI 全绿；建议按
“纯 ID 预留”合并，detector / `esp32p4_boards[]` / 标题映射由后续 PR 补齐。

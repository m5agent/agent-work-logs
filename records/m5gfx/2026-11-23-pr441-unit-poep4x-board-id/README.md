# M5GFX #441: Add Unit PoEP4X board id.

- 日期：`2026-11-23`
- 结果：`REVIEW`（code-level verification；上游 CI 39/39 PASS，hardware / virtual-device 均 `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5GFX#441](https://github.com/m5stack/M5GFX/pull/441)，作者 TinyuZhao，英文，OPEN；
  评审前 comments / reviews 均为 0，无 m5agent 回复
- 源码：`m5stack/M5GFX` PR head `bb02d2e7cef83214fd3e54e2dcfd4c52ac51268e`
  （base `43a87193f898f998edf79c5fb99b166d11ee1eaf` = 当前 develop tip；diff 仅 `src/lgfx/boards.hpp` +1 行）
- 环境：macOS arm64 只读源码核对 + 本机 `g++` 静态断言编译；
  本机 Device Service 36 个 profile 中 ESP32-P4 只有 `tab5`，无 Unit PoE-P4 / PoE-P4X profile

## 结论

没有发现需要阻止合并的问题。该 PR 是板卡 ID 的纯预留，取值、位置与命名都符合本文件既有做法。

- `board_M5UnitPoEP4X = 158` 是 `board_M5StampP4XHub = 157` 之后的下一个非显示 ID；
  外部显示段仍从 `board_M5AtomDisplay = 192` 开始，158 落在非显示区间内。
- 与现有值不冲突：`board_M5UnitPoEP4`（148）、157、`board_M5UnitPoEP4DisplayOut`（201）
  均为不同值；host 侧 `static_assert` 编译通过（exit 0）。
- 命名与同族一致：`board_M5UnitPoEP4`（148）加 `X` 后缀，与 `board_M5StampP4X`（156）
  相对 `board_M5StampP4`（150）的写法一致。
- 影响面只有一行枚举，当前树内没有其他代码引用该枚举，因此不改变任何既有运行时行为。

## 关键证据

- `evidence/pr441.diff`：相对 base 的唯一改动（1 file，+1 line）；保留 git 原始空上下文行
  （行首一个空格），因此 `git diff --cached --check` 对该证据文件报 1 处 trailing whitespace，
  其余记录文件检查通过。
- `evidence/code-facts.txt`：boards.hpp 的 ID 区间、新枚举的全部引用、以及 fixed-board
  查表失败路径（`detection_package.inl:65-86`、`M5GFX.cpp:910-929`）。
- `evidence/host-check.txt`：`g++ -std=c++17 -Wall -Wextra -Werror -I src -fsyntax-only`
  编译含 5 条 `static_assert` 的最小 TU，exit 0。
- `evidence/precedent.txt`：同作者此前的纯 ID 预留提交（148 于 f4923a7，157 于 8d036e1）。
- `evidence/pr-status.txt`：评审前评论/评审为 0，head/base，CI 39/39 SUCCESS（含
  `host` 板卡检测测试与 `translation unit consistency`）。
- `evidence/environment.txt`：设备 profile 盘点与未做虚拟设备验证的原因。

## 文件

- `report.md`：完整报告（ID 空间、引用面、fixed-board 行为、先例、影响面、未覆盖项）
- `run.json`：结构化记录
- `evidence/`：上列原始证据

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 Unit PoE-P4X 实物，也未做上电/显示验证。
- virtual-device validation：`NOT RUN`。改动只是一个未被引用的枚举常量，没有可执行的运行时
  路径；本机唯一 ESP32-P4 profile 是 `tab5`，且无 Unit PoE-P4X 模型。即便构建固定
  board 158 的固件，也只会走到“unsupported board”分支，不能验证产品行为。
- 后续的 detector / `esp32p4_boards[]` 条目 / fixture / SDL 标题映射：`NOT RUN`（不在本 PR 范围）。
- 只做代码级核对；编译与板卡检测测试结论来自上游 CI，未在本机复跑该工作流。

## 已发布回复

- 待发布（发布后回填评论永久链接）。

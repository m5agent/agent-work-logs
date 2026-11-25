# M5Unified PR #448：新增 M5UnitPoEP4X 支持

- 日期：`2026-11-25`
- 结果：`REVIEW`（code-level verification：源码核对 + 4 组 esp32p4 构建；
  hardware / virtual-device 均 `NOT RUN`）
- 工作类型：`pr_review`
- 条目：[m5stack/M5Unified#448](https://github.com/m5stack/M5Unified/pull/448)
  「Add M5UnitPoEP4X support.」，作者 TinyuZhao，英语标题、正文为空，OPEN；
  评审前 comments / reviews 均为 0，无 m5agent 回复
- 源码版本：`m5stack/M5Unified` PR head `6167c9230205071433aa7ea727bb403e55b3db82`
  （base develop `dae3b5d04e6ad5f91ac72a89da09d427a0e20543`）；
  `M5GFX` develop `e7cae681dd5ec6707b5c174a6b75cb5061c3f3d9`、
  发布 tag `0.3.0` = `28d47949bdc84f30881623476f555398e2194313`
- 环境：macOS arm64、ESP-IDF v6.1（`fff9895`）、`esp32p4` target；
  本机 Device Service 36 个 profile 中无 PoE-P4 / PoE-P4X，唯一 ESP32-P4 型号是 `tab5`；
  Docker 镜像存在但 daemon 元数据只读，改用本机 ESP-IDF

## 结论

改动本身是机械对齐已有的 `board_M5UnitPoEP4` 处理，没有发现复制错误或语法问题：
内/外 I2C 引脚、GPIO45 按键输入与 rawstate、关机时 GPIO15-17 拉高、以及 LT8912B
Display Out 挂载条件，四处都与 148 的既有实现一一对应。在 M5GFX develop 下，
`examples/Test/build_test` 对 esp32p4 构建通过。

但有两点在合并前需要作者确认或协调：

1. **当前没有任何路径会把 `_board` 置为 158。** M5GFX develop 里
   `board_M5UnitPoEP4X = 158` 只有枚举（`src/lgfx/boards.hpp:87`），没有
   `board_desc_t` / detector：`src/board_detect/m5/esp32p4.inl` 仍只描述
   `board_M5UnitPoEP4`（148），也没有开放的 M5GFX PR 补 detector。因此
   `M5.begin()` 不可能自动得到 158，本 PR 新增的四个分支只能通过
   `-DBOARD_ID=158` 或 `cfg.fallback_board = board_M5UnitPoEP4X` 到达。
   若期望插上就能识别，需要 M5GFX 侧先补 detector；若本意就是固定板号，
   建议在 PR 说明里写清这一使用方式。
2. **已发布的 M5GFX 没有这个 ID，构建会失败。** 三个依赖声明都是
   `M5GFX >= 0.3.0`，而 0.3.0 没有 158。PR head 在 esp32p4 上分别搭配
   M5GFX 0.3.0 tag 和 registry 自动解析出的 `m5stack/m5gfx 0.3.0` 构建，
   都报 4 处 `'board_M5UnitPoEP4X' is not a member of 'm5::board_t'`；
   同一套构建在 base develop 配 0.3.0 下 0 错误，在 M5GFX develop 下通过。
   所以这不是 PR 的语法问题，而是发布顺序/依赖下限问题：M5Unified 新版本
   必须要求一个包含 158 的 M5GFX 发布，或等 M5GFX 先发版。

次要：`examples/Basic/HowToUse/HowToUse.ino:329` 的板名映射仍只有
`board_M5UnitPoEP4`，加上 X 会更便于看日志（不影响功能）。

## 关键证据

- `evidence/pr-448.json`、`evidence/pr-448.diff`：PR 元数据与完整 diff（3 files，+8 -2）。
- `evidence/source-facts.txt`：158 只存在于 M5GFX develop 的 boards.hpp；0.3.0 无；
  develop 无 PoEP4X detector；M5Unified 内 148 的四处处理点。
- `evidence/build-matrix.txt`：四组构建（A 通过 / B、D 失败 / C 通过）。
- `evidence/build-030-errors.txt`：B 与 D 的编译诊断原文（含 registry 解析行）。
- `evidence/pr-status.txt`：PR 状态、CI 37/37 SUCCESS、36 个设备 profile 盘点。
- `evidence/environment.txt`：编译器与依赖版本。

构建矩阵（`idf.py set-target esp32p4 && idf.py build`）：

| # | M5Unified | M5GFX | 结果 |
| --- | --- | --- | --- |
| A | PR head `6167c92` | develop `e7cae68` | 通过，1148 步，app bin 432080 B |
| B | PR head `6167c92` | 0.3.0 tag `28d4794` | 失败，4 处 158 未定义 |
| C | base `dae3b5d` | 0.3.0 tag `28d4794` | 通过，0 错误，app bin 430320 B |
| D | PR head `6167c92` | registry `m5stack/m5gfx 0.3.0` | 失败，同 B |

## 文件

- `report.md`：完整评审、代码事实、构建矩阵、影响面与未覆盖项
- `run.json`：结构化记录
- `evidence/`：PR 元数据、源码事实、构建摘要与诊断、环境、设备盘点

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 Unit PoE-P4X 实物，未做上电、显示、
  按键、关机 LED 行为验证。
- virtual-device validation：`NOT RUN`。本机 Device Service 的 36 个 profile 中没有
  PoE-P4 / PoE-P4X（唯一 P4 型号 `tab5` 无法代表该板的 pin map 与 LT8912B 通路），
  无法导入固件复现这些分支。
- 引脚映射正确性：`NOT RUN`。内/外 I2C（1/0、54/53）、LED 15-17、按键 45 是从 148
  复制的；`docs.m5stack.com` 目前没有 `Unit_PoE-P4X` 页面（404），无法用官方资料核对，
  需作者确认与 P4X 原理图一致。
- Arduino/PlatformIO 依赖解析（`library.properties` / `library.json` 的 >=0.3.0）
  未单独跑构建；只用 ESP-IDF 组件管理器复现了同一下限问题。
- 合并、关闭、approve、push 或修改他人仓库：`NOT RUN`（只发一条评论）。

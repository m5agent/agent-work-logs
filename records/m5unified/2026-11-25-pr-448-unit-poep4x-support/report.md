# M5Unified PR #448「Add M5UnitPoEP4X support.」评审报告

## 背景

- 来源：[m5stack/M5Unified#448](https://github.com/m5stack/M5Unified/pull/448)，作者 TinyuZhao，
  2026-11-25 创建，base `develop`，正文为空，评审前 0 评论、0 review。
- 关联：[m5stack/M5GFX#441](https://github.com/m5stack/M5GFX/pull/441)（同一作者，2026-11-23 合并）
  只往 `boards.hpp` 添加了 `board_M5UnitPoEP4X = 158`。
- 目标：核对本 PR 是否确实让 M5Unified 支持 Unit PoE-P4X，以及是否存在编译/依赖或行为缺口。

## 结论

改动与既有 `board_M5UnitPoEP4` 处理方式完全对齐，未发现复制错误、遗漏分支或语法问题，
在 M5GFX develop 下可以正常构建。但“支持”目前是休眠状态，且与已发布 M5GFX 不兼容：

1. M5GFX 侧只有枚举，没有 detector / `board_desc_t`，`M5.begin()` 不可能得到 158；
   新分支只能靠 `BOARD_ID=158` 或 `cfg.fallback_board` 进入。
2. 三个依赖清单的下限 `M5GFX >= 0.3.0` 指向的发布版没有 158；已实测在 esp32p4 上
   编译失败，而同一构建在 base 上通过。

## 代码事实

### 改动（3 files，+8 -2）

- `src/M5Unified.hpp:462-465`：Display Out 挂载条件由
  `_board == board_M5UnitPoEP4` 扩为 `... || _board == board_M5UnitPoEP4X`，
  注释同步为 “PoEP4 / PoEP4X”。
- `src/M5Unified.inl:146`：`_pin_table_i2c_ex_in` 复制 148 行：
  `GPIO_NUM_1 / GPIO_NUM_0 / GPIO_NUM_54 / GPIO_NUM_53`。
- `src/M5Unified.inl:2071`：`_setup_pinmap` 内把 GPIO45 设为 input（与 148 相同）。
- `src/M5Unified.inl:3230`：`update()` 的按键 rawstate 分支，读 GPIO45 低有效。
- `src/utility/Power_Class.inl:2424`：`Power_Class::_powerOff()` 中 GPIO15-17
  输出高电平（与 148 相同）。

上述 switch 分支都在 `#if defined (CONFIG_IDF_TARGET_ESP32P4)` 内，不影响非 P4 目标。

### 可达性

`M5Unified::begin()` 的板号来自 `fixed_board`（`BOARD_ID`）、detector、
`cfg.fallback_board`、`getCandidateBoard()` 或默认 fallback（`src/M5Unified.hpp:383-401`）。
M5GFX develop 的 `src/board_detect/m5/esp32p4.inl` 只有 `desc_unitpoep4`（148）
和 `unitpoep4_detector`，没有 158 的描述符或 candidate 条目；`git grep PoEP4X`
在 M5GFX develop 只命中 `boards.hpp` 一行。因此四条新路径在默认配置下不可达。

### 依赖下限

- `library.json`: `"M5GFX": ">=0.3.0"`
- `library.properties`: `depends=M5GFX (>=0.3.0)`
- `idf_component.yml`: `m5stack/m5gfx: version: ">=0.3.0"`

M5GFX `0.3.0`（tag `28d4794`）`boards.hpp` 无 `board_M5UnitPoEP4X`；develop
仍声明 `version=0.3.0`，也就是没有可用的版本号来区分“含 158 的 develop”。

## 构建验证

环境：ESP-IDF v6.1 `fff9895`，riscv32-esp-elf 15.2.0，target `esp32p4`，
工程 `examples/Test/build_test`，命令 `idf.py set-target esp32p4 && idf.py build`。
（ESP-IDF 以目录名作组件名，因此 checkout 目录分别命名为 `M5Unified` / `M5GFX`。）

| # | M5Unified | M5GFX | 结果 |
| --- | --- | --- | --- |
| A | PR head `6167c92` | develop `e7cae68` | PASS，`Project build complete`，1148 步，app 432080 B，sha256 `fa65e1a8…` |
| B | PR head `6167c92` | 0.3.0 tag `28d4794` | FAIL，4 处 `'board_M5UnitPoEP4X' is not a member of 'm5::board_t'` |
| C | base `dae3b5d` | 0.3.0 tag `28d4794` | PASS，0 错误，app 430320 B，sha256 `1e750e75…` |
| D | PR head `6167c92` | 无本地 M5GFX，registry 解析 | FAIL，解析到 `m5stack/m5gfx (0.3.0)`，同样 4 处错误 |

B 的 4 个位置：`M5Unified.inl:146`、`:2071`、`:3230`、`Power_Class.inl:2424`。
C 与 B 只差 M5Unified 的 base/PR，说明失败由本 PR 引入；D 说明普通组件管理器用户
（即使不手动 checkout M5GFX）会直接踩到。

上游 CI 在 PR head 为 37/37 SUCCESS，但工作流会按分支名 clone M5GFX develop，
所以 CI 绿灯不能覆盖“配已发布 M5GFX”的组合。

## 影响面与兼容性

- 非 ESP32-P4 目标不受影响（新增分支都在 P4 条件编译内）。
- 配 M5GFX develop：可编译；但 158 只能通过固定板号进入，默认不改变任何板的行为。
- 配已发布 M5GFX 0.3.0：所有 esp32p4 构建失败，影响面是“升级 M5Unified 后 P4 项目编不过”。
- 修复方向（由作者/维护者决定）：M5GFX 补 158 的 detector 或明确固定板号用法；
  M5Unified 发布时把 M5GFX 下限提到包含 158 的版本，并在 M5GFX 发版之后再发。

## 验证边界

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS / FAIL（按依赖版本） | 四组 esp32p4 构建 |
| transport | NOT RUN | 无设备 |
| device_response | NOT RUN | 无设备 |
| data_behavior | NOT RUN | 无设备 |
| visual_or_physical | NOT RUN | 无设备（显示、LED、按键均未观测） |

- hardware validation：`NOT RUN`，无 Unit PoE-P4X 实物。
- virtual-device validation：`NOT RUN`，Device Service 36 个 profile 无 PoE-P4/P4X。
- 引脚映射：无法用公开资料核对（`Unit_PoE-P4X` 文档页 404），需作者确认。
- Arduino/PlatformIO 的版本解析未单独构建，只用 IDF 组件管理器复现了同一 `>=0.3.0` 下限。

## 风险与回滚

无代码写入、无上游改动，因此无回滚动作。评审结论仅覆盖上表 build 层与源码事实。

## 拟发布回复（英文，与条目语言一致）

见 `review-comment.txt`；发布后回填 URL。

## 后续

- 若作者补充 M5GFX detector 或提高依赖下限，可复跑 A/B/D 三组构建确认。
- 若提供 P4X 引脚说明，可补代码级核对；实机验证仍需硬件。

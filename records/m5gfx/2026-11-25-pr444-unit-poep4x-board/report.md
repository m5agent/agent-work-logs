# M5GFX #444 评审报告：Add Unit PoEP4X board.

## 背景

- 条目：m5stack/M5GFX#444，作者 TinyuZhao，2026-11-25 06:09Z 创建，OPEN，正文为空。
- 前置：#441 已把 `board_M5UnitPoEP4X = 158` 加入 `src/lgfx/boards.hpp` 并合并
  （2026-11-23）。#441 的评审已说明：只加枚举时该 ID 还不可选，后续需要
  descriptor / `esp32p4_boards[]` / fixture / 标题映射。本 PR 正是这个后续。
- 目标：让 M5UnitPoEP4X 作为一个独立板卡被 M5GFX 识别（fixed board 路径），
  并让 `getBoardName()` 返回 `M5UnitPoEP4X`。
- 评审范围：只读 diff + 本地 host 测试；不改上游、不 close、不 push。

## 改动

2 文件，+8 行，无删除：

1. `src/board_detect/m5/esp32p4.inl`
   - 新增 `desc_unitpoep4x`，复用 `unitpoep4_detail::gpio_pins`（31, 52），
     `no_power()` / `no_reset()` / `no_shared_sd()` / `no_display_pins()` /
     `no_internal_i2c()` / `no_options()`，与 `desc_unitpoep4` 同构，只改 id/name。
   - `esp32p4_boards[]` 新增 `{ &desc_unitpoep4x, construct_displayless,
     "board_M5UnitPoEP4X", nullptr }`。
2. `src/M5GFX.cpp`
   - `getBoardName()` 的 switch 增加 `case board_M5UnitPoEP4X: "M5UnitPoEP4X"`。

## 验证

### 1. 上游 CI

PR head `f65875a` 的 run 45558545815（Board detection host tests）结论 failure。
唯一失败的是 `package_p4`：

```
Descriptor snapshot mismatch: p4
Aborted (core dumped)
package_p4: failed
C++ test programs: 1 failed
C++ test programs: 33 passed
```

其余状态项（Arduino / ESP-IDF / catalog / translation unit consistency 等）均为 SUCCESS。

### 2. 本地复现

用 `test/board_detect/run.sh` 的同一条 C++11 命令，在 `/tmp/m5gfx444`（PR head）编译
`package_p4.cpp` 并运行：

- PR head `f65875a`：`Descriptor snapshot mismatch: p4`，Abort trap 6，rc 134。
- merge-base `e7cae68`：`p4: 6 full descriptions match`，`P4 packages: 72 cases passed`，rc 0。

失败来自 `test/board_detect/support/snapshot.hpp:check()`：它把 `esp32p4_boards[]` 的完整
descriptor 序列化后与 `test/board_detect/fixtures/p4.txt` 逐字节比较；新增表项必然改变
序列化结果，因此必须同步 fixture。这不是产品代码缺陷，而是 PR 漏提交生成产物。

### 3. 缺失的 fixture

用 `M5GFX_UPDATE_SNAPSHOTS=1` 重新生成后，`p4.txt` 只多出 7 行：

```
+158 M5UnitPoEP4X 0
+power -1 1 0 0 0 0 0
+reset 0 -1 0 0 0 0
+sd -1 -1 -1 -1 -1
+display -1 -1 -1 -1 -1 -1 -1
+i2c -1 -1 -1 hold [] ops [31,52,] options[]
+entry construct_displayless board_M5UnitPoEP4X 0 0
```

插入位置在 `M5UnitPoEP4` 的 entry 之后、`M5StampP4` 之前，与 `esp32p4_boards[]` 的顺序一致。

同仓库先例：提交 `824da9b`（Add M5StamP4XHub board support）在新增 P4 表项的同时更新了
`test/board_detect/fixtures/p4.txt`（+10 行），说明 fixture 更新是表项改动的固定配套。

### 4. 补 fixture 后的回归

在 PR head 加上上述 7 行、不改其他文件，运行完整 host 套件：

```
P4 packages: 72 cases passed
package_p4: passed
...
C++ test programs: 34 passed
rc=0
```

即当前 PR 的唯一 CI 阻塞项就是这份 fixture。

### 5. fixed-board 与自动识别

用 host probe（`evidence/probe.cpp`，链接生产 `esp32p4.inl` 与
`detection_package.inl`）验证：

- `select_fixed_board(board_M5UnitPoEP4X)` 返回新表项：
  `id=158`、`name=M5UnitPoEP4X`、`construct == construct_displayless`。
  因此 `M5GFX::config.fixed_board = board_M5UnitPoEP4X` 是一条可执行路径
  （`M5GFX.cpp:907-929`）。
- `in_detector_members=0`：`esp32p4_detectors` 中没有任何 detector 把
  `desc_unitpoep4x.def.id` 列为 member。`unitpoep4_detector_t::members_` 只有
  `desc_unitpoep4`，其 PHY ID 判定（0x0243 / 0x0C54）也不区分 X。
  所以自动识别只能返回 `board_M5UnitPoEP4`，X 只能显式 fixed board 选中。

这一条作为非阻塞问题请作者确认：如果 X 与 PoE-P4 在软件上确实不可区分，fixed-board-only
就是合理设计；如果 X 有独立签名（例如 P4 chip revision），则需要额外 detector / 门控。

## 影响面与兼容性

- 新增表项只影响 P4 板卡列表、`select_fixed_board(158)` 和标题映射；不改任何既有板卡的
  detector、pin scope 或构造路径。
- `desc_unitpoep4x` 与 `desc_unitpoep4` 除 id/name 外完全一致，复用同一 GPIO scope；
  `construct_displayless` 不创建 display parts，符合无屏 unit 的定位。
- 补 fixture 只是测试期望值同步，无运行时影响。

## 环境

- macOS 26.5.1 arm64，Apple clang 21.0.0。
- 源码：`m5stack/M5GFX` PR head `f65875a`；基线 merge-base `e7cae68`。
- 本机 Device Service：36 个 profile，ESP32-P4 仅 `tab5`，无 Unit PoE-P4/P4X。

## 未覆盖项与风险

- hardware validation `NOT RUN`：无 Unit PoE-P4X 实物；未验证上电、PHY 链路、固件启动。
- virtual-device validation `NOT RUN`：无对应 device profile，无法导入/启动。
- 真实设备上的自动识别结果、`getBoardName()` 输出未实测，只做了源码与 host probe 核对。
- 上游其余 38 项 SUCCESS 未在本地逐项复跑。

## 回滚方式

评审结论不涉及代码回滚。若作者不接受 fixed-board-only 设计，可只保留 #441 的枚举，
撤回本 PR；补 fixture 的方案本身可用 `git checkout -- test/board_detect/fixtures/p4.txt`
撤销。

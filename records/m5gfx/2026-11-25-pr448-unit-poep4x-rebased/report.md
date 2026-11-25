# M5GFX #448 评审报告：Add Unit PoE-P4X board support（rebased #444）

## 背景

- 条目：https://github.com/m5stack/M5GFX/pull/448 ，作者 ainyan03，2026-11-25 13:04Z
  创建，OPEN、非 draft，正文英文，0 评论 0 review（评审前）。
- 该 PR 是 #444（作者 TinyuZhao）的单 commit cherry-pick：`#445 / #446 / #447` 改了
  catalog 测试清单与 editor bundle，#444 无法直接 merge。
- m5agent 在 #444 上曾提出四点意见（catalog 生成物、descriptor 快照、自动识别可达性、
  M5Unified pin 表）；作者已修改，本次复核 rebase 后是否保持。
- 评审范围：只读 diff + host 测试 + 独立行为探针；不改上游、不 close、不 push。

## 现状与关键事实

- head `d8d7b959d0292ef2cf9c86f9ce5003cbc011f718`，父提交即 base `develop`
  `488d621`（`Merge pull request #447`），因此 diff 就是全部改动：14 文件，+916/−15。
- 冲突解决：`extras/board_spec/test/board_spec.test.js` 的 unverified 名单新增
  `m5unitpoep4x`，同时 `m5stack_corematrix` 仍在 verified 侧（不在 unverified 数组里），
  `develop` 的迁移没有被回退。
- 新增 `extras/board_spec/boards/m5unitpoep4x.json`：`legacy_board_id` 158、与
  `m5unitpoep4.json` 相同的 pins/buses/connectors；`official_name_verified` 与
  `spec.links` 因产品页仍 404 而省略，测试按 unverified 名单接受。
- `src/board_detect/m5/esp32p4.inl`：
  - `desc_unitpoep4x` 与 `desc_unitpoep4` 同构，复用 `unitpoep4_detail::gpio_pins`
    （31/52），`construct_displayless`，并加入 `esp32p4_boards[]`。
  - `unitpoep4_detector_t::members_` 从 `{148}` 扩为 `{148,158}`；
    `revision_desc()` 用 `io::chip_revision() >= 300` 选 148/158，与
    `tab5_family_detector_t` 逐行同构（同一常量、同一 `warn_hint_mismatch` 语义）。
  - 提示冲突时 `warn_hint_mismatch` 只在 `ctx.attempt == 0` 记录一条 `ESP_LOGW`，
    随后 `result->assign(desc)`，与 Tab5 行为一致；框架层没有二次用 hint 覆盖结果
    （`detection_integration.inl` 只把 hint 传入 `detect_board`）。
- 生成物：`detector_order.json`、`detector_order_constraints.hpp`、Pin 表
  （esp32p4.inl/json）、`test/board_detect/generated/detector_probe_pins.hpp`
  （`{31,32,52}` 对 `{148,158}`）、`fixtures/p4.txt`（新增 7 行 158 描述块）、
  editor bundle 均已重生成。

## 验证

环境：macOS arm64，Apple clang，Node 26.13.1；M5GFX 克隆于 `/tmp` 的 PR head；
M5Unified `develop` 副本 `6eb276a`（含 158 行）用于 Pin 表比对。

### 1. 仓库自带 host 测试（PR head）

```
$ node cli/spec.js check
check passed: 64 board(s), 91 resolved combination(s)

$ sh test/board_detect/run.sh
C++ test programs: 34 passed

$ M5GFX_UPDATE_SNAPSHOTS=1 sh test/board_detect/run.sh   # 快照重生成
git status --porcelain                                    # 空 → 无漂移
```

### 2. 依赖对齐（M5Unified develop）

```
$ node cli/spec.js compare-pintable --m5unified <M5Unified develop>
M5Unified pin-table comparison passed: 56 board(s), 2800 value(s), 4 target(s)
```

M5Unified#448（Add M5UnitPoEP4X support）已于 2026-11-25T03:07Z 合并，`develop`
`src/M5Unified.inl:146` 含 `{ board_t::board_M5UnitPoEP4X, 1, 0, 54, 53 }`，
因此不存在“M5GFX 先于 M5Unified 合并导致 Pin 表比对失败”的顺序依赖。

### 3. 完整 node 套件

```
$ M5UNIFIED_PATH=<M5Unified develop> npm test
tests 221 / pass 221 / fail 0 / skipped 0
```

未设置 `M5UNIFIED_PATH` 时该用例自动 skip（5 项 skipped），不能据此判断 Pin 表一致。

### 4. 独立行为探针（补上游 fixture 的空白）

`test/board_detect/fixtures/p4.txt` 只是 `esp32p4_boards[]` 的 descriptor 序列化，
158 条目与 revision 无关，因此 in-tree 用例并不执行 revision 分支。为验证本次真正
新增的逻辑，`code/poep4x_gate_probe.cpp` 用 `host_hardware::input` 实现一个最小
MDIO slave（每次寄存器读 19 次 `pin_read`：TA Z、TA 0、16 位数据、尾位；先读 2 再读 3），
并用 `host_chip::revision` 逐例切换：

```
revision   0 -> board 148
revision 100 -> board 148
revision 200 -> board 148
revision 299 -> board 148
revision 300 -> board 158
revision 301 -> board 158
revision 399 -> board 158
hint 148 on revision 300 -> board 158, warnings 1
hint 158 on revision 0   -> board 148, warnings 1
hint 158 on revision 300 -> board 158, warnings 0
no PHY response -> rejected for revision 0 and 300
PoE-P4X gate probe: 12 cases passed
```

结论：边界 299/300 正确；冲突 hint 被覆盖且恰好告警一次；一致 hint 不告警；
无 PHY 响应时 confirm 返回 false。该探针是评审侧临时工程，未提交到上游。

### 5. 上游 CI

`gh pr checks 448`：40 项全部 pass，含 `host`（58s）、
`Catalog and generated sources`（18s）、`translation unit consistency`、
ESP32-P4 的 IDF 5.4.3/6.0.2 与 Arduino 3.1.3/3.3.13/4.0.0，以及
`ChipVariant=postv3` / `prev3`。

## 影响面与兼容性

- 新增 board id 158 的完整路径（catalog → descriptor → detector member → board entry
  → title），不改变既有 148 的探测条件（PHY ID 0x0243/0x0C54、引脚 31/52 未变）。
- 探测顺序约束未变（`stampp4xhub`、`tab5` 仍排在 `unitpoep4` 之前）。
- 保存 hint 为 148 的 PoE-P4X 设备会被改判为 158 并打印一条 warning；这是本次有意
  引入的行为，与 Tab5/Tab5X 一致。

## 未覆盖与风险

- `hardware validation` `NOT RUN`：无 PoE-P4/P4X 实机，PHY 上电链路、真实 revision
  读取与 `M5.begin()` 返回值未观测；158 的实机识别证据来自作者 #444 自测（v3.2）。
- `virtual-device validation` `NOT RUN`：本机 Device Service 36 个 profile 中 ESP32-P4
  只有 `tab5`，无 PoE-P4/P4X 模型。
- 上游缺 revision 门限的 host 用例（作者已在正文列为 follow-up）；建议把本探针的场景
  以 `package_p4.cpp` 风格补进上游。
- catalog 的 `verified: "datasheet"` 继承自 PoE-P4，产品页公开后应复核。

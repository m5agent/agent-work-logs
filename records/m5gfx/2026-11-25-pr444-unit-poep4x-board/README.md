# M5GFX #444: Add Unit PoEP4X board.

- 日期：`2026-11-25`
- 结果：`FAIL`（PR 按当前提交不能通过 host CI：fixture 未更新；已本地复现并验证
  7 行修复后 34/34 通过。证据等级 host-level test + code-level verification；
  hardware / virtual-device 均 `NOT RUN`）
- 工作类型：`pr-review`
- 条目：[m5stack/M5GFX#444](https://github.com/m5stack/M5GFX/pull/444)，作者 TinyuZhao，
  英文，OPEN；评审前 comments / reviews 均为 0，无 m5agent 回复
- 源码：`m5stack/M5GFX` PR head `f65875a55b3922afaa1695be428344c6d0e92904`
  （merge-base `e7cae681dd5ec6707b5c174a6b75cb5061c3f3d9`；base 分支 tip
  `5873de4e43b727fab651b71f615246267a816720`，已含 #443 合并；PR diff 仍只有 2 文件 +8 行）
- 关联：[#441](https://github.com/m5stack/M5GFX/pull/441)（同作者，2026-11-23 合并）
  只加了 `board_M5UnitPoEP4X = 158`；本 PR 是后续的 descriptor / 表项 / 标题接线
- 环境：macOS 26.5.1 arm64，Apple clang 21.0.0；本机 C++11 host 板卡检测测试；
  本机 Device Service 36 个 profile 中 ESP32-P4 只有 `tab5`，无 Unit PoE-P4/P4X profile

## 结论

代码改动本身正确：`board_M5UnitPoEP4X`（158）的 descriptor、`esp32p4_boards[]` 表项和
`M5GFX.cpp` 标题映射彼此一致，`fixed_board` 路径可以选中该板（probe 返回 id 158 /
`M5UnitPoEP4X` / `construct_displayless`）。但 PR 不能按当前状态通过 CI：

- **阻塞项**：`test/board_detect/fixtures/p4.txt` 没有随新表项更新。上游 `host` job 在
  `package_p4` 以 `Descriptor snapshot mismatch: p4` 失败（run 45558545815）。
- 本地在 PR head 上复现同一失败（abort，rc 134）；同测试在 merge-base `e7cae68` 通过
  （72 cases）。补上 7 行 fixture 后，`sh test/board_detect/run.sh` 为 34/34 通过。
- 需要的 fixture 内容见 `evidence/fixture-fix.diff`（`158 M5UnitPoEP4X 0` 起的 7 行，
  与 `M5UnitPoEP4` 的 descriptor 完全同构）。

**非阻塞观察**：`unitpoep4_detector_t::members_` 只列 `desc_unitpoep4`，没有任何 detector
引用 `desc_unitpoep4x`，所以自动识别仍只会返回 `board_M5UnitPoEP4`；X 只能通过
`M5GFX::config.fixed_board = board_M5UnitPoEP4X` 选中。已在评论中请作者确认这是否为预期；
如果 X 有可区分的签名（例如芯片 revision），则还需要 detector 或 revision 门控。

## 关键证据

- `evidence/host-failure.txt`：上游 run 45558545815 的失败行与 head SHA。
- `evidence/local-repro.txt`：PR head 复现（失败）、merge-base 基线（72 cases 通过）、
  补 fixture 后全量 host 测试 34/34 通过。
- `evidence/fixture-fix.diff`：缺失的 7 行 fixture diff。
- `evidence/probe.cpp` / `evidence/probe.txt`：`select_fixed_board(158)` 返回新表项；
  `in_detector_members=0`。
- `evidence/device-profiles.txt`：本机 36 个 profile 的盘点与 P4 只有 `tab5` 的事实。
- `evidence/pr444.diff`、`evidence/pr-status.txt`：改动范围、PR 状态、CI 结果。
  `pr444.diff` 保留 git 原始空上下文行（行首一个空格），因此
  `git diff --cached --check` 对该证据文件报 1 处 trailing whitespace，其余记录文件通过。

## 文件

- `report.md`：完整报告（改动、CI 失败链路、本地复现与修复验证、可达性分析、边界）
- `run.json`：结构化记录
- `evidence/`：上列原始证据

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 Unit PoE-P4X 实物，未做上电、PHY 识别或显示验证。
- virtual-device validation：`NOT RUN`。本机 Device Service 没有 Unit PoE-P4/P4X profile
  （P4 只有 `tab5`），无法构建/启动对应虚拟设备。
- 未验证真实 PoE-P4X 上的自动识别结果与 `getBoardName()` 输出；标题映射只做了源码核对。
- 上游 CI 其余 38 项 SUCCESS 来自 GitHub 状态汇总，未在本机逐项复跑。

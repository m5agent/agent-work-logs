# M5GFX PR #450（board_spec 用 generate / verify 简化新增板卡）只读评审

- 日期：`2026-11-26`
- 结果：`PASS`（评审 + host-level test + code-level verification），运行时验证 `NOT RUN`
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/M5GFX/pull/450
- 源码版本：`m5stack/M5GFX @ a092ea5a85b047263e409448d6d33a7650b2141e`（base `develop` `28b8a5c310075d6432a2096c7444dce5e5c7013f`，即 #449 合并后的 tip）
- 环境：macOS arm64、Apple clang、Node 26.13.1；仓库自带 Node + C++ host 测试；本机 Device Service 有 36 个 profile，但本改动没有运行时路径，未使用

## 结论

PR #450 把“新增板卡”收敛为 `npm run generate` + `npm run verify` 两步，并把生成物、
`targets.json` 与测试清单去列表化。按四组改动逐项复核后**未发现阻塞问题**：

- `generate` 幂等（生成后工作区无差异），`verify` 依次执行 catalog check、Node 测试与
  C++ host 测试，并在失败后继续跑完全部三项；带 `M5GFX_UPDATE_SNAPSHOTS=1` 也不会更新快照。
- 20 个变更的生成头文件（`src/board_detect/m5/generated/*.hpp` 19 个 +
  `test/board_detect/generated/detector_probe_pins.hpp`）去掉注释行后声明集合与 base 完全相同，
  只有 `esp32p4_board_data.hpp` 出现命名空间顺序变化（两个 PoE 单元移到文件末尾），
  其余仅改“Regenerate … npm run generate”注释。
- 新增一个无屏 trial 板（catalog JSON + `boards.hpp` + `esp32c6.inl` descriptor/表项）后，
  只跑 `generate` + `verify` 即通过，确认无需再改 `targets.json` 或测试文件。
- `dist/board_spec_editor.html` 取消跟踪后，仓库内没有残留引用；`npm run editor` 仍能在
  本地构建 bundle，且被 `.gitignore` 忽略。
- 上游 CI 39/39 通过，含 `host` 与 `Catalog and generated sources`。

两条非阻塞措辞建议（代码与 README 行为一致，只是 PR 描述口径偏宽）：

1. “targets.json records exceptions only” 与 “trial board passes without editing targets.json”
   会让读者以为显示类板卡也不需要条目；实际 `board_id_coverage.test.js` 仍要求非
   `construct_displayless` 构造器必须有非空 `wiring_fields`（移除 `m5atoms3` 条目即报
   可操作的失败信息）。
2. 正文 “Generated declarations are ordered by catalog ID” 与实现/README 不一致：
   有 `targets.json` 条目的板卡保持条目顺序，无条目的才按 catalog ID 追加。
   另外新增的根级 `.github/PULL_REQUEST_TEMPLATE.md` 会应用到全部 PR，不只板卡改动。

## 关键证据

- `node cli/spec.js check`：head `64 board(s), 91 resolved combination(s)`，base 相同。
- `npm test`：head 238 项（233 pass / 0 fail / 5 skip，skip 为缺 M5Unified checkout）；
  base 222 项（217 pass / 0 fail / 5 skip）→ 新增 16 项，无失败。
- `sh test/board_detect/run.sh`：head 与 base 均为 `C++ test programs: 34 passed`。
- `npm run verify`：三项全 passed；显式 `CXX=/nonexistent-compiler` 时按设计失败，
  本地无编译器时 skip 并给出提示。
- 失败诊断：缺失/过期/多余生成物分别列出并附重生成命令；快照故意改一行后输出
  `fixtures/c6.txt:3 expected/actual` 与 `M5GFX_UPDATE_SNAPSHOTS=1` 提示。
- trial 板：`check passed: 65 board(s), 92 resolved combination(s)`，238 项 0 fail，
  改动文件只有 catalog JSON、`boards.hpp`、`esp32c6.inl`。
- 上游 CI：39/39 pass。
- 日志：`evidence/verify.log`、`evidence/check_and_node_tests.log`、
  `evidence/host_cpp_tests.log`、`evidence/base_control.log`、`evidence/declaration_order.log`、
  `evidence/addition_workflow.log`、`evidence/snapshot_diagnostic.log`、
  `evidence/editor_and_generate.log`、`evidence/ci_checks.log`。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：命令输出与对照日志
- `code/addition_workflow.sh`：trial 板与显示构造器守卫的可重建脚本

## 未覆盖项

- `hardware validation` `NOT RUN`：改动不涉及固件运行路径，没有实机可观测对象。
- `virtual-device validation` `NOT RUN`：本机 Device Service 确有 `cores3`、`sticks3`、
  `cardputer-adv`、`paperdiy` 等 profile，但本 PR 不构建、不烧录、不运行固件，
  虚拟设备没有可采集的启动/画面/外设信号。
- M5Unified live pin table 对比在本机 `NOT RUN`（缺 M5Unified checkout，5 项 skip）；
  base 上同样 skip，因此不影响 A/B 对照结论。

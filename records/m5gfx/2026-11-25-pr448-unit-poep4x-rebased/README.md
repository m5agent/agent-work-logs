# M5GFX PR #448（Unit PoE-P4X rebased #444）只读评审

- 日期：`2026-11-25`
- 结果：`PASS`（评审与 host 验证），运行时验证 `NOT RUN`
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/M5GFX/pull/448
- 源码版本：`m5stack/M5GFX @ d8d7b959d0292ef2cf9c86f9ce5003cbc011f718`（base `develop` `488d621`）
- 环境：macOS arm64、Apple clang、Node 26.13.1、本地 C++11 board-detect host harness、本机 Device Service；不写内网端点

## 结论

PR #448 把 #444 的单 commit 干净地 rebase 到当前 `develop`，冲突只落在
`extras/board_spec/test/board_spec.test.js` 的 unverified 名单，且已正确保留
`develop` 把 `m5stack_corematrix` 移入 verified 的改动。新增 catalog 项、
descriptor、`esp32p4_boards[]`、标题映射、Pin 表与快照互相对齐；#444 评审中提出的
“没有 detector 成员引用 X、自动识别不可能返回 158”已在本次提交中关闭：
`unitpoep4_detector` 同时持有 148/158，按 `io::chip_revision() >= 300` 选择，与
Tab5/Tab5X 完全同构。仓库自带 host 测试与 CI 全部通过；另有独立 host 探针验证了
revision 边界（299/300）、hint 覆盖与告警次数。未发现阻塞问题。

## 关键证据

- 构建或运行：`node cli/spec.js check` → 64 boards / 91 combinations；
  `sh test/board_detect/run.sh` → 34 programs passed；
  `M5GFX_UPDATE_SNAPSHOTS=1` 重生成后 `git status` 无差异。
- 依赖对齐：M5Unified `develop`（`6eb276a`）已含 158 行，`compare-pintable`
  → 56 boards / 2800 values / 4 targets 通过。
- 测试套件：`M5UNIFIED_PATH=<develop> npm test` → 221 passed、0 failed、0 skipped。
- 行为探针：`code/poep4x_gate_probe.cpp` 模拟 MDIO slave，12 用例通过；revision
  0/100/200/299 → 148，300/301/399 → 158；hint 148+rev300 → 158 且 warnings=1；
  hint 158+rev0 → 148 且 warnings=1；hint 一致时 warnings=0；无 PHY 响应被拒绝。
- 上游 CI：40 项检查全部 pass，含 `host`、`Catalog and generated sources`、
  ESP32-P4 IDF 5.4.3/6.0.2 与 Arduino P4（含 postv3/prev3 ChipVariant）。
- 日志：`evidence/node_tests.log`、`evidence/host_cpp_tests.log`、
  `evidence/poep4x_gate_probe.log`、`evidence/ci_checks.log`、
  `evidence/device_profiles.log`、`evidence/m5unified_develop.log`。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：命令输出、PR diff、M5Unified 版本与设备 profile 清单
- `code/poep4x_gate_probe.cpp`、`code/build_and_run.sh`：可重建的 revision 门限探针

## 未覆盖项

- `hardware validation` `NOT RUN`：本机没有 Unit PoE-P4/P4X 实机；真实 PHY 链路、
  上电时序与 M5Unified 运行时板号未在本机观测，相关结论来自作者自测（#444 中 v3.2
  被识别为 158）与代码/主机验证。
- `virtual-device validation` `NOT RUN`：本机 Device Service 共 36 个 profile，其中
  ESP32-P4 只有 `tab5`（ST7121/ST7123），没有任何 PoE-P4/P4X 模型，无法创建匹配的
  虚拟设备。
- 上游仓库内仍缺 revision 门限的 host 用例（作者已在正文列为 follow-up）；本记录的
  探针只是评审侧独立验证，未推送到上游分支。

# M5GFX PR #422 复核：`(void)family` 修正后两种日志配置均通过

- 日期：`2026-11-16`
- 结果：`PASS`（上一轮报告的 debug 日志启用时编译失败已在 `70713a6` 消除）
- 工作类型：`pr_review`（follow-up recheck）
- 来源：[m5stack/M5GFX#422](https://github.com/m5stack/M5GFX/pull/422)
- 源码版本：base `28d47949bdc84f30881623476f555398e2194313`（0.3.0）；
  head `70713a658b5b71aaf2fe73fee949796125e9d2e8`（上一轮为 `ab6cf1c`，作者已 amended）
- 验证层级：**host-level test**（仓库自带 `test/board_detect/run.sh` + 合同桩编译矩阵）
- 硬件 / 虚拟设备：`NOT RUN`（编译期问题，无运行时行为可观测；本机无 Arduino ESP32 core / ESP-IDF 源码）
- 上一轮记录：[2026-11-16-pr422-board-detect-log-warnings](../2026-11-16-pr422-board-detect-log-warnings/README.md)（`FAIL`，保留不改）
- GitHub 回复：PR #422 本轮复核评论（2026-11-16，英文单条）
- 环境：macOS 26.5.1，Apple clang 21.0.0（`clang-2100.1.1.101`）

## 结论

作者把 `family` 声明恢复，并在其后加 `(void)family;`。该语句在两个方向上都能成立：

- 日志参数被丢弃（≈ `CORE_DEBUG_LEVEL=0`）时，`(void)family;` 记作一次使用，`-Wunused-variable` 消失；
- 日志参数被求值（≈ `CORE_DEBUG_LEVEL>=4`）时，stage=1（`:55`）与 stage=2（`:67`）的
  `ESP_LOGD` 都引用已声明的 `family`，编译通过。

上一轮的阻塞点（stage=2 引用未声明标识符）已不存在。`transaction.inl` 与上一轮评审的版本
是同一 blob（`ef803e8`，两次 head 的父提交同为 `a410256`，该提交只改了
`detector_runner.inl`），因此上一轮的 7 场景等价性结论继续有效，无需重跑。

## 关键证据

- `sh test/board_detect/run.sh`：base `33 passed`，head `33 passed`。这正是 `ab6cf1c`
  上会以 `detector_runner.inl:66:80: error: use of undeclared identifier 'family'` 中止的配置。
- 编译矩阵（33 个 TU × {参数求值, 参数丢弃}，`-Wall -Wextra -O2 -std=c++11`）：
  head 四种组合 0 错误；参数丢弃时 base 在两个文件各出现 29 次告警，head 为 0。
- `detector_runner.inl` 相对 base 只新增 `(void)family;` 一行；`(void)` 转型无副作用。
- diff 全量为 `3+/3-`（detector `+1`，transaction `2+/3-`），不是字面意义上的“仅加一行”。

## 附注（不阻塞）

`CORE_DEBUG_LEVEL=0` 下同形态的“仅日志使用”变量仍存在于 P4 文件：
`src/board_detect/m5/esp32p4.inl:227` 的 `revision` 只被 `ESP_LOGW` 使用，而 level 0 下
`ESP_LOGW` 同样被编译掉。base 与 head 表现相同（P4 相关 TU 各 4 条），属于既有问题，
不在本 PR 声称的两条告警范围内。

## 文件

- [report.md](report.md)：方法、命令、结果表、未覆盖项
- [run.json](run.json)：结构化状态
- [code/recheck.sh](code/recheck.sh)：双 ref × 双日志模式的编译矩阵脚本
- [evidence/compile-matrix.txt](evidence/compile-matrix.txt)：矩阵原始输出
- [evidence/host-test-28d4794.txt](evidence/host-test-28d4794.txt)：base host 测试
- [evidence/host-test-70713a6.txt](evidence/host-test-70713a6.txt)：head host 测试
- [evidence/source-pins.json](evidence/source-pins.json)：commit、blob 与文件 SHA256

## 未覆盖项

- 完整 Arduino/ESP-IDF 构建（`CORE_DEBUG_LEVEL=4/5`）：`NOT RUN`。本机没有 Arduino ESP32
  core 或 ESP-IDF 源码；用合同桩求值 `ESP_LOGx` 参数复现同一预处理形态。
- CI：`70713a6` 的 5 个 workflow 均为 `action_required`（首次贡献者审批），GitHub 上没有
  check 结果；上述为本地执行证据。
- 硬件 / 虚拟设备：`NOT RUN`，无运行时行为可观测。
- 未修改 M5GFX，未向作者分支 push，未关闭 PR。

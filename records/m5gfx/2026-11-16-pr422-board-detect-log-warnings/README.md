# M5GFX PR #422：日志变量告警修复在 DEBUG 日志启用时编译失败

- 日期：`2026-11-16`
- 结果：`FAIL`（PR head 在 `ESP_LOGD` 启用时无法编译；仓库自带 host 测试命令在第一个 TU 中止）
- 工作类型：`pr_review`
- 来源：[m5stack/M5GFX#422](https://github.com/m5stack/M5GFX/pull/422)
- 源码版本：base `28d47949bdc84f30881623476f555398e2194313`（0.3.0）；
  PR head `ab6cf1c538db39a0c2108840ebddddeca828fdbe`
- 验证层级：**host-level test**（仓库自带 `test/board_detect/run.sh`、
  `M5GFX_BOARD_DETECT_IO_HEADER` 合同桩编译矩阵、快照恢复运行时等价检查）
- 硬件 / 虚拟设备：`NOT RUN`（这是编译期与日志宏问题，没有可观测的运行时行为；本机没有
  Arduino/ESP-IDF 工具链）
- GitHub 回复：发布后补充（单条英文评论，PR 保持 OPEN）
- 环境：macOS，Apple clang 21.0.0（`clang-2100.1.1.101`）

## 结论

PR 想消除 `CORE_DEBUG_LEVEL=0` 时两个“变量只被日志使用”的告警。其中
`transaction.inl` 的改写等价，可以保留；`detector_runner.inl` 的改写不成立：

- base 在 `detector_runner.inl:51-52` 声明 `const char* family`，除 stage=1 的
  `ESP_LOGD`（`:54`）外，stage=2 的 `ESP_LOGD`（`:66`）也用它。
- PR 删除了声明，只把表达式内联进 stage=1 的调用（head `:52-55`），stage=2 的
  `family`（head `:66`）没有任何替代。
- 当 `ESP_LOGD` 参数被求值（`CORE_DEBUG_LEVEL>=4`，或任何启用 DEBUG 日志的构建）时，
  宏展开后引用未声明的 `family`，编译失败；只有日志参数被整体编译掉
  （`CORE_DEBUG_LEVEL=0`）时才恰好通过。PR 正是按 `CORE_DEBUG_LEVEL=0` 验证的，
  因此这个回归在自己的验证配置里不可见。

仓库 CI 使用的 `sh test/board_detect/run.sh` 会强制包含把 `ESP_LOGD` 参数传入
`quiet_log(...)` 的桩头文件，参数始终求值。该命令在 base 上 `33` 个程序全部通过，
在 PR head 上第一个 TU 就报 `detector_runner.inl:66:80: error: use of undeclared
identifier 'family'`。

## 关键证据

- 告警矩阵（`-Wall -Wextra`，日志参数丢弃 ≈ `CORE_DEBUG_LEVEL=0`）：base 6 条告警，
  含报告中的 `transaction.inl:59`（`missing_pin` set-but-not-used）与
  `detector_runner.inl:51`（`family` unused）；PR 降到 4 条，这两条消失。日志参数
  求值时 base 干净，PR 报上述未声明错误。
- 仓库自带 host 测试：base `C++ test programs: 33 passed`；PR head 在
  `test/board_detect/airq_generated.cpp` 的首个编译单元即失败（`run.sh` 的 `set -e`
  会立即中止）。
- `transaction.inl` 等价性：`pin < 0` 在 `:63`（head `:62`）已被 `continue` 跳过，
  因此 `missing_pin` 一旦被赋值必为 `>= 0`，用 `missing_pin < 0` 作哨兵与原来的
  `bool missing` 等价。7 个运行时场景（含 `pin=0`、`-1`、多个缺失引脚）两版日志输出
  逐字相同。
- `signature()` / `confirm()` 是 `const` 虚函数（`board_detect.hpp:432-433`），
  `members` 为 `const board_def_t* const*`（`:444`），所以把 family 表达式移到
  stage=2 调用里也没有副作用；当前 PR 只是漏掉了第二处。

## 建议

阻塞项只需改 `detector_runner.inl` 一处，二选一：

1. 保留声明并在其后加 `(void)family;`（C++11 可用，两处日志继续共用）；
2. 把同一三元表达式也内联进 stage=2 的 `ESP_LOGD`（head `:66`）。

`transaction.inl` 部分无需改动。

不阻塞的附注：若目标是“纯 `-Wextra` + `CORE_DEBUG_LEVEL=0` 零告警”，还有 4 条
`-Wunused-parameter`（`ops.inl:19-20`、`prepare.inl:8`）未处理；仓库 `run.sh` 用
`-Wno-unused-parameter` 关闭了它们，所以 CI 不会显示。它们不在本 PR 声称的两条告警
范围内，可另开改动。

## 文件

- [report.md](report.md)：代码事实、验证方法、结果表与未覆盖项
- [run.json](run.json)：结构化状态
- [code/run.sh](code/run.sh)：编译矩阵与运行时等价检查
- [code/stub_io.hpp](code/stub_io.hpp)：`M5GFX_BOARD_DETECT_IO_HEADER` 合同桩
- [code/tu.cpp](code/tu.cpp)：包含真实 `board_detect.inl` 的编译单元
- [code/tx_check.cpp](code/tx_check.cpp)：快照恢复运行时检查
- [evidence/compile-matrix.txt](evidence/compile-matrix.txt)：告警/错误原始输出
- [evidence/host-test-master.txt](evidence/host-test-master.txt)：base host 测试通过
- [evidence/host-test-pr-head.txt](evidence/host-test-pr-head.txt)：PR host 测试失败
- [evidence/tx-equivalence.txt](evidence/tx-equivalence.txt)：7 个场景对照输出
- [evidence/source-pins.json](evidence/source-pins.json)：commit 与文件 SHA256

## 未覆盖项

- **硬件验证 / 虚拟设备验证**：`NOT RUN`。缺陷发生在预处理/编译期，运行设备不能观测；
  本机也没有 Arduino/ESP-IDF 构建链，无法把 M5GFX 编进固件或最小 sketch。
- **完整 Arduino/ESP-IDF 构建（`CORE_DEBUG_LEVEL=4/5`）**：`NOT RUN`。用仓库自带 host
  测试命令与合同桩代替；两者都走真实的 `board_detect` 源码。
- **Linux g++**：`NOT RUN`。本轮用 Apple clang；错误是标准 C++ 的未声明标识符，
  CI 的 g++ 预期同样失败，但未实际执行。
- 未修改 M5GFX，未向作者分支 push，未关闭 PR。

# M5GFX PR #422 复核报告（head `70713a6`）

## 1. 背景

上一轮评审（[记录](../2026-11-16-pr422-board-detect-log-warnings/README.md)）在
`ab6cf1c` 上发现：`detector_runner.inl` 删除了 `family` 声明，但 stage=2 的 `ESP_LOGD`
仍在引用它，因此只有日志参数被预处理掉时才能编译。作者随后把修正 amend 进第二个提交
（head 变为 `70713a6`），并称已用 `sh test/board_detect/run.sh`（33 passed）与
`CORE_DEBUG_LEVEL=0` 的 Arduino 构建（零告警）验证。

本轮只复核这一处新变更，不重复上一轮结论。

## 2. 变更内容

`git diff 28d4794..70713a6`：

- `src/board_detect/detector_runner.inl`：新增一行 `(void)family;`（`:53`），声明
  `family`（`:51`）恢复，stage=1（`:55`）与 stage=2（`:67`）的 `ESP_LOGD` 共用该变量。
- `src/board_detect/transaction.inl`：`bool missing` 改为 `missing_pin < 0` 哨兵。
  该文件 blob 为 `ef803e8`，与上一轮评审时的版本相同（`ab6cf1c` 与 `70713a6` 的父提交
  都是 `a410256`，而 `a410256` 只改 `detector_runner.inl`），因此上一轮的 7 场景等价性
  结果直接沿用。

全量 diffstat：`3 insertions(+), 3 deletions(-)`。

## 3. 环境与命令

- 主机：macOS 26.5.1，Apple clang 21.0.0（`clang-2100.1.1.101`）。
- 仓库：[m5stack/M5GFX](https://github.com/m5stack/M5GFX)，base `28d4794`（0.3.0），
  head `70713a6`；两者分别以 detached worktree 检出，互不污染。
- host 测试：`sh test/board_detect/run.sh`（C++11、`-O2 -Wall -Wextra
  -Wno-unused-function -Wno-unused-parameter -pedantic`，强制包含会求值
  `ESP_LOGx` 参数的 `support/native_devices_io.hpp`）。
- 编译矩阵：对 33 个 `test/board_detect/*.cpp` 逐 TU 编译，`-Wall -Wextra -O2
  -std=c++11 -pedantic`，两种日志模式：
  - `expanded`：仓库桩，`ESP_LOGD(...)` → `quiet_log(__VA_ARGS__)`，参数求值；
  - `discarded`：`discard_io.hpp` 把 `ESP_LOGx(...)` 重定义为 `((void)0)`，参数整体
    丢弃，等价于 Arduino `CORE_DEBUG_LEVEL=0` 的宏形态（该级别下 `ESP_LOGE/W/I/D`
    全部为 no-op）。
  脚本见 [code/recheck.sh](code/recheck.sh)。

## 4. 结果

| ref | 日志模式 | 编译失败 TU | `detector_runner.inl` 告警 | `transaction.inl` 告警 |
| --- | --- | --- | --- | --- |
| `28d4794` | expanded | 0 | 0 | 0 |
| `28d4794` | discarded | 0 | 29（`:51 unused variable 'family'`） | 29（`:59 missing_pin set but not used`） |
| `70713a6` | expanded | 0 | 0 | 0 |
| `70713a6` | discarded | 0 | 0 | 0 |

- 计数为“出现该告警的编译单元数”（29 个 TU 包含 `board_detect.inl`）。
- host 测试：`28d4794` → `C++ test programs: 33 passed`；`70713a6` → 同上。
  `ab6cf1c` 在同一命令下首个 TU 即因未声明 `family` 失败，本轮不再复现。
- 原始输出：[evidence/compile-matrix.txt](evidence/compile-matrix.txt)、
  [evidence/host-test-70713a6.txt](evidence/host-test-70713a6.txt)。

## 5. 同形态遗留项

`discarded` 模式下，base 与 head 都还有 `src/board_detect/m5/esp32p4.inl:227` 的
`unused variable 'revision'`（P4 相关 TU 各 4 条）：`revision` 只被 `ESP_LOGW` 使用，
而 level 0 下 `ESP_LOGW` 也被编译掉。该文件仅在 `CONFIG_IDF_TARGET_ESP32P4` 时被
`src/M5GFX.cpp` 引入，所以非 P4 的 Arduino 构建看不到；它先于本 PR 存在，不属于本 PR
声称的两条告警。若目标是“所有板型 level 0 零告警”，可另开改动。

## 6. 未覆盖项与风险

- 完整 Arduino/ESP-IDF 构建（`CORE_DEBUG_LEVEL=4/5`）：`NOT RUN`。本机无 Arduino ESP32
  core、无 ESP-IDF 源码；合同桩的宏求值形态与被测行为一致，但不等价于真实工具链构建。
- 其它编译器（Linux g++、xtensa-esp32-elf-g++）：`NOT RUN`。本轮只用 Apple clang；
  修复本身是标准 C++ 的 `(void)` 使用，风险低但未实测。
- 运行时行为：本轮与上一轮均无运行时可观测项；`(void)family;` 不生成代码，
  `family` 的初始化在 base 中已存在，因此不改变运行时。
- 硬件 / 虚拟设备：`NOT RUN`（编译期问题，无需设备）。
- 风险：无。修改不触碰公共 API，不改变日志文本与判定逻辑。

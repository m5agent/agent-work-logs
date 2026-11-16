# 报告：M5GFX PR #422 board_detect 日志变量告警修复评审

## 1. 问题来源与目标

作者 Junbo-Zheng 在 [m5stack/M5GFX#422](https://github.com/m5stack/M5GFX/pull/422)
提出两处 `src/board_detect/` 改动，目标是消除以 `-Wall -Wextra` 和
`CORE_DEBUG_LEVEL=0` 构建时的两条告警：

```text
src/board_detect/transaction.inl:59:9: warning: variable 'missing_pin' set but not used
src/board_detect/detector_runner.inl:51:19: warning: unused variable 'family'
```

PR 描述声明 “No behavior change”。base 为 master
`28d47949bdc84f30881623476f555398e2194313`（0.3.0），head 为
`ab6cf1c538db39a0c2108840ebddddeca828fdbe`，两个 commit：

- `a410256` board_detect: drop redundant missing flag in restore_to_snapshot
- `ab6cf1c` board_detect: inline family name into ESP_LOGD call

本轮目标是只读核对：告警是否真的消除、改写是否等价、在不同日志级别下是否仍可编译。
未修改上游代码、未 push、未关闭 PR。

## 2. 代码事实

### 2.1 `detector_runner.inl`：`family` 不止一处使用

base 版本：

```cpp
51:      const char* family = (detector->members && detector->members[0])
52:                         ? detector->members[0]->name : "empty";
53:      const bool enter_confirm = detector->signature(ctx);
54:      ESP_LOGD(tag, "stage=1 family=%s detector=%p match=%d", family, ...);
...
65:      const bool confirmed = detector->confirm(ctx, &family_result);
66:      ESP_LOGD(tag, "stage=2 family=%s detector=%p match=%d board=%u name=%s", family, ...);
```

head 版本删掉了 `51-52` 的声明，把同一表达式内联进 stage=1 的调用（head `:52-55`），
但 stage=2 的调用（head `:66`）仍原样引用 `family`：

```cpp
66:      ESP_LOGD(tag, "stage=2 family=%s detector=%p match=%d board=%u name=%s", family,
```

`ESP_LOGD` 在 `CORE_DEBUG_LEVEL=0` 时被预处理为空语句，实参整体丢弃，所以未声明的
`family` 不会进入编译；当 DEBUG 日志启用（Arduino-ESP32 的 `CORE_DEBUG_LEVEL>=4`，
或等价地 `LOG_LOCAL_LEVEL>=ESP_LOG_DEBUG`）时实参被展开，编译报
`use of undeclared identifier 'family'`。作者只在 `CORE_DEBUG_LEVEL=0` 下验证，
因此没有看到这个回归。

`signature()` 与 `confirm()` 都是 `const` 虚函数（`board_detect.hpp:432-433`），
`members` 是 `const board_def_t* const*`（`:444`），因此把 family 表达式移到
stage=2 调用处也没有副作用——当前实现只是漏掉了第二处。

### 2.2 `transaction.inl`：哨兵改写等价

base：

```cpp
58:    bool missing = false;
59:    int missing_pin = -1;
...
63:      if (pin < 0) { continue; }  // an unused optional signal
...
72:      if (!found && !missing) { missing = true; missing_pin = pin; }
...
87:    if (missing)
88:    {
89:      ESP_LOGE("board_detect", "restore_to_snapshot pin=%d is absent from snapshot", missing_pin);
90:    }
```

head：

```cpp
58:    int missing_pin = -1;
...
62:      if (pin < 0) { continue; }  // an unused optional signal
...
71:      if (!found && missing_pin < 0) { missing_pin = pin; }
...
86:    if (missing_pin >= 0)
87:    {
88:      ESP_LOGE("board_detect", "restore_to_snapshot pin=%d is absent from snapshot", missing_pin);
89:    }
```

`:62`/`:63` 的 `if (pin < 0) continue;` 保证被记录的 `pin` 一定 `>= 0`，因此
`missing_pin` 一旦被赋值就不可能仍是 `-1`；`pin=0` 也能正确记录
（`0 < 0` 为假，`0 >= 0` 为真）。`missing_pin` 的类型仍是 `int`，`pins` 是
`std::int8_t*`，取值范围 `-128..127`，不存在哨兵冲突。

## 3. 验证方法

### 3.1 仓库自带的 host 测试

M5GFX 仓库自带 `test/board_detect/run.sh`，CI 的 `BoardDetect.yml` 就是执行这条命令。
它用 `-DM5GFX_BOARD_DETECT_IO_HEADER="support/detect_io.hpp"` 替换设备 I/O，并
`-include support/native_devices_io.hpp`，后者把 `ESP_LOGD` 定义为
`host_hardware::quiet_log(__VA_ARGS__)`——参数始终求值。编译 flag 为
`-std=c++11 -O2 -Wall -Wextra -Wno-unused-function -Wno-unused-parameter -pedantic`。

分别在 base 与 PR head 的干净 checkout 上执行：

```sh
CXX=c++ sh test/board_detect/run.sh
```

### 3.2 告警矩阵（日志参数丢弃 vs 求值）

仓库 host 桩始终求值日志参数，无法复现 `CORE_DEBUG_LEVEL=0` 的告警。为此使用
[`code/stub_io.hpp`](code/stub_io.hpp)：它实现 `detect_io.hpp:135` 文档化的
`M5GFX_BOARD_DETECT_IO_HEADER` 合同，仅改变 `ESP_LOGx` 宏：

- 默认：`ESP_LOGx` 展开为 `do {} while (0)`，参数丢弃（等价 `CORE_DEBUG_LEVEL=0`）；
- `-DHM_LOG_LEVEL=4`：参数传给一个空的 variadic 函数，参数被求值（等价 DEBUG 日志开启）。

`code/tu.cpp` 直接 `#include "board_detect/board_detect.inl"`，编译命令：

```sh
c++ -std=gnu++17 -Wall -Wextra -fsyntax-only \
    -I<checkout>/src -I. -DM5GFX_BOARD_DETECT_IO_HEADER='"stub_io.hpp"' tu.cpp
```

两个 checkout 各编译两种宏配置，记录告警/错误。

### 3.3 运行时等价检查

`code/tx_check.cpp` 只包含 `board_detect.hpp`、`ops.inl` 和 `transaction.inl`
（不含出问题的 `detector_runner.inl`），用真实
`detection_gpio_snapshot_t::restore_to_snapshot()`，日志被捕获为字符串。7 个场景：

| 快照 | 请求恢复的引脚 | 预期 |
| --- | --- | --- |
| `{5}` | `{-1,-1}` | 负值全部跳过，无错误日志 |
| `{5}` | `{5}` | 已存在，无错误日志 |
| `{5}` | `{7}` | 记录缺失引脚 7 |
| `{5}` | `{0}` | 记录缺失引脚 0（哨兵边界） |
| `{5}` | `{7,9}` | 只记录第一个缺失引脚 7 |
| `{5,0}` | `{0}` | 已存在，无错误日志 |
| `{5}` | `{-1,7}` | 跳过 -1，记录 7 |

两个版本分别编译运行，逐条比较日志文本。

## 4. 结果

### 4.1 编译矩阵

| checkout | 日志参数丢弃（≈`CORE_DEBUG_LEVEL=0`） | `ESP_LOGD` 启用（参数求值） |
| --- | --- | --- |
| base `28d4794` | 6 条告警：`ops.inl:19/20`（3 条 unused-parameter）、`transaction.inl:59`、`detector_runner.inl:51`、`prepare.inl:8` | 干净 |
| PR head `ab6cf1c` | 4 条告警：`ops.inl:19/20`、`prepare.inl:8`；报告的两条已消失 | **编译失败**：`detector_runner.inl:66:80: error: use of undeclared identifier 'family'` |

原始输出：[`evidence/compile-matrix.txt`](evidence/compile-matrix.txt)。这说明 PR
在目标配置（日志参数丢弃）下确实消除了两条告警，但在 DEBUG 日志开启时引入了编译回归。

### 4.2 仓库 host 测试

- base `28d4794`：`C++ test programs: 33 passed`，退出码 0。
- PR head `ab6cf1c`：第一个 TU `test/board_detect/airq_generated.cpp` 编译失败，
  `run.sh` 因 `set -e` 立即中止，退出码 1。

```text
In file included from .../test/board_detect/support/runtime.hpp:13:
.../src/board_detect/detector_runner.inl:66:80: error: use of undeclared identifier 'family'
   66 |       ESP_LOGD(tag, "stage=2 family=%s detector=%p match=%d board=%u name=%s", family,
1 error generated.
```

原始输出：[`evidence/host-test-master.txt`](evidence/host-test-master.txt)、
[`evidence/host-test-pr-head.txt`](evidence/host-test-pr-head.txt)。

### 4.3 `transaction.inl` 等价性

两个版本 7 个场景的输出逐字相同：[`evidence/tx-equivalence.txt`](evidence/tx-equivalence.txt)。
包括 `pin=0`（哨兵边界）与负值（上游已跳过）场景，未观察到行为差异。

## 5. 评估与建议

**阻塞项**：`detector_runner.inl` 的 stage=2 日志仍需要 `family`。最小修法二选一：

1. 恢复 `const char* family = ...;` 并在声明后加 `(void)family;`，让它在
   `CORE_DEBUG_LEVEL=0` 下算作“已使用”，两处 `ESP_LOGD` 继续共用；
2. 把同一三元表达式也内联进 stage=2 的 `ESP_LOGD`（head `:66`）。

因为 `signature()`/`confirm()` 是 `const` 成员且 `members` 为 const 限定指针，
方案 2 的求值时机变化没有可观测副作用；方案 1 改动更小、可读性更好。

**`transaction.inl`**：等价改写，无需修改。

**不阻塞的附注**：若目标是“纯 `-Wextra` + `CORE_DEBUG_LEVEL=0` 零告警”，仍有 4 条
`-Wunused-parameter`：`ops.inl:19`（`device`）、`ops.inl:20`（`elapsed_ms`、`ready`）、
`prepare.inl:8`（`why`）。它们与本次两条同源（参数只被日志使用），但仓库 `run.sh`
用 `-Wno-unused-parameter` 关闭，CI 不会显示；PR 描述也只提了两条。可作为后续独立
改动，不构成本 PR 的阻塞项。

**CI 现状**：head SHA `ab6cf1c` 的 `Board detection host tests` 等 workflow 均为
`action_required`（首次贡献者待批准），尚未执行；一旦批准，该 workflow 会在上述位置
失败。PR 当前 `MERGEABLE`，需要先修编译问题。

## 6. 未覆盖项与风险

- **硬件验证**：`NOT RUN`。缺陷在预处理/编译期，运行设备不能观测；本机也没有对应
  M5GFX 固件可烧。
- **虚拟设备验证**：`NOT RUN`。原因同上；本机没有 Arduino/ESP-IDF 工具链，无法为
  模拟器构建最小 M5GFX sketch。`M5GFX_BOARD_DETECT_IO_HEADER` 的 host 合同桩是
  仓库为这类检查提供的既定路径。
- **完整 Arduino/ESP-IDF 构建（`CORE_DEBUG_LEVEL=4/5`）**：`NOT RUN`。只做了 host
  编译与仓库 host 测试，未产出目标固件。
- **Linux g++**：`NOT RUN`。本轮使用 Apple clang 21；`use of undeclared identifier`
  是标准 C++ 诊断，预期 g++ 同样失败，但未实际执行。
- **风险**：如果维护者只按 `CORE_DEBUG_LEVEL=0` 合并，DEBUG 构建的用户会立刻遇到
  编译错误；`BoardDetect.yml` 也会在批准后失败。建议合并前先修 `family`。

## 7. 结论

PR 的 `transaction.inl` 改写等价且达到消除告警的目的；`detector_runner.inl` 改写遗漏了
stage=2 的第二处 `family` 引用，导致 DEBUG 日志启用时编译失败。证据等级为
**host-level test**（仓库自带 host 测试 + 合同桩编译矩阵 + 运行时等价检查），
硬件与虚拟设备验证未执行。

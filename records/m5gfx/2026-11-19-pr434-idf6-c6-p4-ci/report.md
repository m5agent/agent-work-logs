# M5GFX #434 评审报告：为 C6/P4 增加 ESP-IDF 6.0.2 构建

## 1. 背景与目标

M5GFX #432 把 FIFO 深度的取值源从 `soc_caps.h` 的 `SOC_*` 切到 `hal/i2c_ll.h` 的
`I2C_LL_*`，修好了 ESP-IDF 6.x 下 LP 端口按 HP 深度（32）分块写入 LP FIFO（16）的
问题；#433 又给「LP 端口存在但两个深度宏都不存在」的情况加了 `#error`。但 #433 的
评审记录里已经指出：`IDFBuild.yml` 的 6.x 作业只有 esp32 / esp32s3，两者都没有 LP
I2C 端口，所以这段代码在 CI 里从未被编译过，当时给出的非阻塞建议是「加 esp32c6 at
6.0.2」。

本 PR #434 就是那条建议的落地，额外把 P4 也加上了。评审要回答三件事：

1. 4 行矩阵改动是否就是全部改动，CI 是否真的通过、有无新告警；
2. 新作业是否真的编译了原来没被编译的 LP I2C 分支（而不是矩阵数字上好看）；
3. PR 正文关于 P4 覆盖 LP GPIO matrix、以及不与 M5Unified CI 重复的说法是否准确。

## 2. 改动范围

`.github/workflows/IDFBuild.yml`，+4/-0，只新增两条矩阵项：

```yaml
          - target: esp32c6
            idf_version: "6.0.2"
          ...
          - target: esp32p4
            idf_version: "6.0.2"
```

- base 是 `develop` 的 `1d4f3f9`（#433 的 merge commit），head `6cee190` 是单一提交。
- 矩阵从 13 个作业变为 15 个作业；`git apply --check` 在 base 上通过，PR 状态
  `MERGEABLE` / `CLEAN`。

## 3. 方法

改动属于构建配置，没有运行时行为，因此不选择实机或模拟设备：任何能编过的配置生成的
代码与 base 完全相同，唯一的观测量是「构建成功/失败」。取证分两层：

### 3.1 host-level：读 PR head 的真实 CI 结果与日志

`gh pr checks 434` 给出 head 上全部 28 项检查；对两个新作业
（`esp32c6 (IDF 6.0.2)` job 135263308585、`esp32p4 (IDF 6.0.2)` job 135263308606）
拉取完整日志，统计 `warning:` / `error:`，并确认
`lgfx_v1_platforms.cpp`（`common.inl` 的宿主翻译单元）确实被编译、产物生成成功。

### 3.2 code-level：按 6.0.2 头文件与构建依赖还原宏状态

从 `espressif/esp-idf` v6.0.2 取 C6/P4 的 `soc_caps.h` 与
`components/esp_hal_i2c/<target>/include/hal/i2c_ll.h`，确认
`SOC_LP_I2C_NUM=(1U)`、`I2C_LL_LP_FIFO_LEN=16`、`SOC_LP_I2C_FIFO_LEN` 在 6.0 已移除；
再结合 M5GFX `CMakeLists.txt` 的 `COMPONENT_REQUIRES ... driver ...`（IDF ≥ 6）与
CI 日志里打印的组件列表，确认 `<driver/i2c_master.h>` 在包含路径上，从而
`LGFX_LP_I2C_NUM` 为 1，`getFifoLen()` 实际编译的是 `I2C_LL_LP_FIFO_LEN` 分支。

## 4. 观察

### 4.1 CI 结果

| 作业 | 结果 | 用时 | 日志 warning / error |
| --- | --- | --- | --- |
| esp32c6 (IDF 6.0.2) | pass | 2m58s | 0 / 0 |
| esp32p4 (IDF 6.0.2) | pass | 3m04s | 0 / 0 |

- 两个作业都出现
  `Building CXX object esp-idf/M5GFX/CMakeFiles/__idf_M5GFX.dir/src/lgfx/v1/lgfx_v1_platforms.cpp.obj`
  与 `Project build complete`，产物分别为 0x584d0 / 0x524b0 字节。
- 同一 run 里既有的 esp32 / esp32s3 6.0.2、5.x 作业也全部通过，没有作业被取消。

### 4.2 宏状态与分支

| 目标 @ 6.0.2 | `SOC_LP_I2C_NUM` | `SOC_LP_I2C_FIFO_LEN` | `I2C_LL_LP_FIFO_LEN` | 结果 |
| --- | --- | --- | --- | --- |
| esp32c6 | `(1U)` | 不存在 | 16 | `#elif I2C_LL_LP_FIFO_LEN` 分支，LP 深度 16 |
| esp32p4 | `(1U)` | 不存在 | 16 | 同上，LP 端口索引为 2 |

- `common.inl:125-130` 的三个条件（`SOC_LP_I2C_NUM > 0`、能找到
  `<driver/i2c_master.h>`、IDF ≥ 5.4）在 6.0.2 的两个目标上都成立。
- M5GFX 组件在 IDF ≥ 6 时 `REQUIRES` 里含 `driver`，CI 日志打印的组件列表同样是
  `...;driver;...`，所以该头文件确实可被 `__has_include` 命中。
- 因为 `I2C_LL_LP_FIFO_LEN` 已定义，#433 的 `#error`（`common.inl:1471-1473`）
  不会触发——这与构建通过一致；该作业因此覆盖的正是 #432/#433 改动所在的分支。

### 4.3 P4 的 LP GPIO matrix

- 6.0.2 的 P4 `soc_caps.h` 有 `SOC_LP_GPIO_MATRIX_SUPPORTED 1`，且
  `driver/lp_io.h` 存在，于是 `common.inl:193-195` 定义 `LGFX_LP_GPIO_MATRIX`，
  `common.inl:1871-1873` 定义 `LGFX_LP_I2C_LEND_PADS`，
  `lp_pads_return()` 走 `lp_gpio_connect_*_signal()`。
- C6 没有该 cap，走 `rtc_gpio_iomux_func_sel()` 分支。PR 正文「P4 额外覆盖 C6 不走的
  LP GPIO matrix 路径」准确。

### 4.4 与 M5Unified 的分工

M5Unified 的 `IDFBuild.yml` 用 5.3 与 6.1 构建 C6/P4；M5GFX 现在补的是 6.0.2，
两边仍无「同芯片 + 同 minor」的重复构建，PR 正文的说明准确。

## 5. 未覆盖项、风险与回滚

- 本地独立重建 `NOT RUN`：本机 Docker 守护进程无法创建容器（containerd 元数据只读），
  没有在 PR 之外重跑 6.0.2 构建；结论依赖 PR 自带 CI 的执行记录与 6.0.2 头文件原文。
  如果要求「不依赖上游 CI」的独立证据，需要在 Docker 可用的机器上跑
  `examples/Test/build_test` 的 `idf.py set-target esp32c6` / `esp32p4` + `idf.py build`。
- hardware validation 不适用；virtual-device validation 结构性不适用（无运行时差异）。
- `#error` 的实际触发路径仍无法由真实 SDK 的 CI 覆盖（需要人为造出缺宏的 SDK）；
  这与 #433 记录的边界一致，不是本 PR 的缺陷。
- 风险很低：只增加矩阵项，不改源码、不改既有作业。回滚即删除这 4 行。

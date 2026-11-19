# M5GFX #434: 用 ESP-IDF 6.0.2 构建 C6/P4，覆盖 LP I2C 分支（CI 构建级验证）

- 日期：`2026-11-19`
- 结果：`PASS`（host-level CI 构建；硬件、虚拟设备对本改动不适用）
- 工作类型：`pr`
- 条目：[m5stack/M5GFX#434](https://github.com/m5stack/M5GFX/pull/434)
  「ci: build ESP32-C6 and ESP32-P4 with ESP-IDF 6.0.2」，作者 ainyan03，英文，OPEN
- 源码：PR head `6cee1901eb7eb0e6bbd44ff6907d98efa44b0b70`，base `develop`
  `1d4f3f992800f7fa5c835dbb74db5c1e6cd1cfff`（即 #433 的 merge commit）
- 环境：GitHub Actions `ubuntu-latest` + `espressif/idf:v6.0.2` 容器（PR 自带 CI）；
  macOS arm64 本机只做只读取证，未做本地独立重建

## 结论

1. 改动只有 `.github/workflows/IDFBuild.yml` 的 4 行矩阵新增（esp32c6 / esp32p4 各加
   一条 6.0.2），没有其它文件变化。head 上 28 项检查全部 `pass`，两个新作业
   `esp32c6 (IDF 6.0.2)` 2m58s、`esp32p4 (IDF 6.0.2)` 3m04s 均成功，作业日志
   `warning:` 与 `error:` 计数都是 0，作者「无新增告警」的说法成立。
2. 覆盖是真实生效的，不只是矩阵数字变化：M5GFX 在 IDF ≥ 6 的 `COMPONENT_REQUIRES`
   里含 `driver`（CI 日志也打印了同一列表），因此 `<driver/i2c_master.h>` 可被找到，
   6.0.2 的 C6/P4 又都有 `SOC_LP_I2C_NUM (1U)`，所以
   `LGFX_LP_I2C_NUM` 解析为 1；6.0.2 的 `hal/i2c_ll.h` 提供
   `I2C_LL_LP_FIFO_LEN 16`，于是 `getFifoLen()` 走的是 #432 引入、
   #433 用 `#error` 兜底的 `I2C_LL_LP_FIFO_LEN` 分支。两个新作业都实际编译了
   `lgfx_v1_platforms.cpp`（`common.inl` 的宿主翻译单元）。
3. PR 正文关于「P4 额外覆盖 LP GPIO matrix 路径」的说法准确：6.0.2 的 P4 有
   `SOC_LP_GPIO_MATRIX_SUPPORTED=1` 且 `driver/lp_io.h` 存在，于是
   `LGFX_LP_GPIO_MATRIX=1`，`lp_pads_return()` 走 `lp_gpio_connect_*_signal()`；
   C6 没有该 cap，走 `rtc_gpio_iomux_func_sel()` 分支。
4. PR 正文关于不与 M5Unified CI 重复的说法也成立：M5Unified 的 C6/P4 作业在 6.1，
   M5GFX 现在补的是 6.0.2，两侧没有同一芯片 + 同一 minor 的重复构建。
5. 无阻塞问题。一条非阻塞提醒：这两个作业只能证明该分支「能编过」，
   `#error` 的实际触发路径（宏缺失）仍无法由真实 SDK 的 CI 覆盖，与 #433 记录一致。

## 关键证据

- `evidence/ci-jobs.txt`：head 上 28 项检查、两个新作业的时间与结论、作业日志中
  `warning:`/`error:` 计数、`lgfx_v1_platforms.cpp` 编译行、组件列表与产物大小。
- `evidence/idf602-lp-caps.txt`：ESP-IDF v6.0.2 的 `soc_caps.h` 与
  `esp_hal_i2c/*/include/hal/i2c_ll.h` 原文行（C6/P4 的 LP 端口数、FIFO 深度、
  P4 的 LP GPIO matrix cap）、`driver/i2c_master.h` / `driver/lp_io.h` 的存在性、
  M5GFX 的 `REQUIRES driver` 与 `common.inl` 对应行号。
- `evidence/diff-scope.txt`：base/head、+4 行差分、矩阵前后对比、
  `git apply --check` 在 base 上通过。
- `patches/0001-ci-idf6-c6-p4.patch`：PR head 的差分。
- 前序分析：`records/m5gfx/2026-11-18-pr433-lp-fifo-error/`（该记录当时建议
  「加 esp32c6 at 6.0.2」，本 PR 就是这条建议的落地，并额外加了 P4）。

## 未覆盖项

- 本地独立重建：`NOT RUN`。本机 Docker 守护进程无法创建容器（containerd 元数据
  存储只读），因此没有在 PR 之外独立跑一遍 6.0.2 构建；改用 PR 自带 CI 日志
  + 6.0.2 头文件原文取证。这不是代码级推测，但也请注意它依赖上游 CI 的执行结果。
- hardware validation：不适用。改动只是 CI 矩阵，不改变任何运行时行为。
- virtual-device validation：不适用，且是结构性的：矩阵变化不产生新的固件行为，
  任何模拟设备上都不可能观察到差异；唯一可观测量是「构建是否成功」。
- `#error` 触发路径：`NOT RUN`，需要人为造出「有 LP 端口、没有深度宏」的 SDK，
  现有 CI 无法覆盖。

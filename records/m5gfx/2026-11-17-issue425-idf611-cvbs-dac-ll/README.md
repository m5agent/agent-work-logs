# M5GFX #425：ESP-IDF v6.1.1 下 esp32 目标的 Panel_CVBS 编译失败（DAC LL 重命名）

- 日期：`2026-11-17`
- 结果：`PASS`（build 层：原失败复现 + 最小补丁全量构建通过；CVBS 运行与实机 `NOT RUN`）
- 工作类型：`issue`
- 条目：[m5stack/M5GFX#425](https://github.com/m5stack/M5GFX/issues/425)
  "ESP-IDF 6.1.1: Panel_CVBS doesn't compile for esp32 (DAC LL APIs renamed)"，
  作者 JC-000，英文，OPEN，取得时评论 0
- 源码：`develop` `b48dce04c80d3e3c9874b7ba946c43d672129c28`；`master`（0.3.0）同一区间的调用完全相同
- 环境：macOS arm64；Docker 镜像 `espressif/idf:v6.1.1`（linux/arm64）；xtensa-esp-elf g++ 15.2.0，
  `-std=gnu++26`；最小 ESP-IDF 应用（`code/`），只把 M5GFX 作为组件编译

## 结论

1. 报告可复现。用 IDF v6.1.1 构建 `esp32` 目标时，`lgfx_v1_platforms.cpp` 在
   `Panel_CVBS.inl` 的 1976 / 1978 / 2037 / 2039 / 2040 行报 5 条 `dac_ll_*` 未声明错误，
   与报告列出的 5 条一致（行号因版本不同有偏移）。
2. 这不是 CVBS 用户才会遇到的问题：`lgfx_v1_platforms.cpp:12` 无条件包含该 `.inl`，
   文件内只按 `CONFIG_IDF_TARGET_ESP32` 区分，所以任何 esp32 目标构建 M5GFX 都会失败。
3. 报告对 API 变化的判断正确。v6.1.1 的 `hal/dac_ll.h` 中
   `dac_ll_power_on/power_down` → `dac_ll_pad_power_on/pad_power_down`，
   `dac_ll_rtc_sync_by_adc` → `dac_ll_sync_by_adc`；
   `dac_ll_digi_enable_dma` 被移除，旧实现同时写 `dac_dig_force` 与 `dac_clk_inv`，
   在 v6.1.1 中拆成 `dac_ll_pad_set_data_source(ch, DAC_DATA_SOURCE_DMA)` 和
   `dac_ll_dma_clk_inv(true)`（IDF 自带 `dac_dma.c` / `dac_common.c` 即这样使用）。
4. 给出并验证了一个最小兼容补丁：以 `ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(6,1,1)` 分支，
   6.1.1 走新 API，旧版本保持原调用。打补丁后 v6.1.1 / esp32 全量构建（1057 步）成功，
   产物 312,304 字节。补丁对 `b48dce0` 通过 `git apply --check`。
5. M5GFX 自己的 `IDFBuild.yml` 矩阵中 esp32 只测到 6.0.2，没有 6.1.x 任务，因此该 CI 全绿
   不能覆盖本次失败；这也解释了为什么只在 v6.1.1 用户侧暴露。

## 关键证据

- 构建（失败）：`evidence/build-unpatched-errors.txt`、`evidence/build-unpatched-fail-idf611-esp32.log`
- 构建（补丁后通过）：`evidence/build-patched-pass-idf611-esp32.log`、`evidence/build-artifact.txt`
- IDF 头文件与驱动用法：`evidence/idf-v611-dac-ll-names.txt`、`evidence/idf-dac-driver-mapping.txt`
- M5GFX 调用点与包含关系：`evidence/m5gfx-cvbs-source-refs.txt`
- CI 矩阵：`evidence/m5gfx-ci-matrix.txt`
- 补丁：`patches/0001-panel-cvbs-idf611-dac-ll.patch`，`evidence/patch-apply-check.txt`
- 条目元数据：`evidence/issue-425.json`
- 已发布回复：<https://github.com/m5stack/M5GFX/issues/425#issuecomment-6928508537>（1 条，Issue 保持 OPEN，代码未改）

## 文件

- `report.md`：根因、映射表、补丁语义、构建过程与边界
- `run.json`：结构化记录
- `code/`：可重建的最小 IDF 工程
- `patches/`：最小兼容补丁
- `evidence/`：原始日志、头文件摘录、CI 矩阵、产物摘要

## 未覆盖项

- hardware validation：`NOT RUN`。没有在 StickC Plus2 等 esp32 机型上烧录并观察 CVBS 输出。
- virtual-device validation：`NOT RUN`。Device Service 与 esp-emulator 都没有 ESP32 DAC/CVBS
  复合视频模型，无法在虚拟设备上执行这条路径；本次问题是编译期错误，运行时也无法在未修复时进入。
- CVBS 运行时行为：`NOT RUN`。补丁只证明可编译、可链接；DAC DMA 通路是否仍输出正确的
  复合视频信号未验证。
- 旧版本回归构建：`NOT RUN`。补丁在 `< 6.1.1` 分支保留原调用，代码内容未变，因此未重跑
  6.1 / 6.0.2 构建。
- Arduino-ESP32 内核路径：`NOT RUN`。本次只验证 ESP-IDF 组件构建。
- 上游合并：未改 M5GFX 代码、未提 PR；补丁仅作为可复现建议。

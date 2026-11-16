# M5GFX #425：ESP-IDF v6.1.1 下 esp32 目标的 Panel_CVBS 编译失败 报告

## 背景

- 来源：<https://github.com/m5stack/M5GFX/issues/425>，作者 JC-000，2026-11-16T20:24:40Z 创建，OPEN。
- 现象：在 `espressif/idf:v6.1.1` 中为经典 `esp32` 构建使用 M5GFX 的工程时，
  `src/lgfx/v1/platforms/esp32/Panel_CVBS.inl` 报 5 条 DAC LL API 未声明错误；
  ESP32-S3 构建正常。作者给出 ESP-IDF 提交 `3e279c2a1df` 与 API 对照表。
- 目标：在声明的 base commit 上复现该构建失败，核对 API 改名事实，并验证一个最小兼容补丁
  能让 v6.1.1 / esp32 构建通过。

## 结论

- 状态：`PASS`（build 层）。原失败在 `develop` `b48dce0` 上复现；打补丁后全量构建成功。
- 根因：ESP-IDF v6.1.1 的 `components/esp_hal_ana_conv/esp32/include/hal/dac_ll.h` 重命名了
  DAC LL API，并移除了 `dac_ll_digi_enable_dma`。M5GFX 的 CVBS 面板仍调用 v6.1 及更早的名字。
- 影响面：`lgfx_v1_platforms.cpp` 无条件包含 `Panel_CVBS.inl`，因此只要 `CONFIG_IDF_TARGET_ESP32`
  被定义，整个 M5GFX 组件就无法编译；不需要实例化 `Panel_CVBS`，也不需要真的使用复合视频。
- 改动范围：仅 `Panel_CVBS.inl` 的 include 与 5 个调用点，使用 IDF 版本守卫；
  对 `< 6.1.1` 的代码路径不产生字节级变化。

## 证据

### 代码或配置

M5GFX 调用点（`b48dce0`，`src/lgfx/v1/platforms/esp32/Panel_CVBS.inl`）：

```text
1976:      dac_ll_digi_enable_dma(false);      // deinit
1978:      dac_ll_power_down(ch);
2037:        dac_ll_power_on(channel);          // init
2039:      dac_ll_rtc_sync_by_adc(false);
2040:      dac_ll_digi_enable_dma(true);
```

包含关系：

```text
src/lgfx/v1/lgfx_v1_platforms.cpp:12: #include "platforms/esp32/Panel_CVBS.inl"
Panel_CVBS.inl:26-28: #if defined (ESP_PLATFORM) ... #if !defined (CONFIG_IDF_TARGET) || defined (CONFIG_IDF_TARGET_ESP32)
```

ESP-IDF 旧/新 API（`components/esp_hal_ana_conv/esp32/include/hal/dac_ll.h`）：

| v6.1 及更早 | v6.1.1 | 说明 |
| --- | --- | --- |
| `dac_ll_power_on(ch)` | `dac_ll_pad_power_on(ch)` | 改名 |
| `dac_ll_power_down(ch)` | `dac_ll_pad_power_down(ch)` | 改名 |
| `dac_ll_rtc_sync_by_adc(v)` | `dac_ll_sync_by_adc(v)` | 改名 |
| `dac_ll_digi_enable_dma(v)` | 无 | 旧实现同时写 `dac_dig_force` 与 `dac_clk_inv` |
| — | `dac_ll_pad_set_data_source(ch, DAC_DATA_SOURCE_DMA)` | 写 `dac_dig_force` |
| — | `dac_ll_dma_clk_inv(v)` | 写 `dac_clk_inv` |

IDF v6.1.1 自己的用法与之对应：

```text
components/esp_driver_dac/dac_common.c:76   dac_ll_pad_set_data_source(chan_id, source);
components/esp_driver_dac/dac_common.c:77   dac_ll_sync_by_adc(false);
components/esp_driver_dac/dac_common.c:78   dac_ll_pad_power_on(chan_id);
components/esp_driver_dac/esp32/dac_dma.c:152  dac_ll_dma_clk_inv(true);
components/esp_driver_dac/esp32/dac_dma.c:193  dac_ll_dma_clk_inv(false);
```

连续模式用 `DAC_DATA_SOURCE_DMA`，单次模式用 `DAC_DATA_SOURCE_DIRECT`，余弦模式用
`DAC_DATA_SOURCE_COSINE`（`dac_continuous.c:381`、`dac_oneshot.c:33`、`dac_cosine.c:137`）。
补丁在 deinit 时选 `DAC_DATA_SOURCE_DIRECT`，对应旧 `dac_ll_digi_enable_dma(false)` 关闭 DMA
数据源后的状态。

补丁核心（完整见 `patches/0001-panel-cvbs-idf611-dac-ll.patch`）：

```c
#if defined (ESP_IDF_VERSION) && ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(6, 1, 1)
      dac_ll_dma_clk_inv(false);
      auto ch = _get_dacchannel(_config_detail.pin_dac);
      dac_ll_pad_set_data_source(ch, DAC_DATA_SOURCE_DIRECT);
      dac_ll_pad_power_down(ch);
#else
      dac_ll_digi_enable_dma(false);
      auto ch = _get_dacchannel(_config_detail.pin_dac);
      dac_ll_power_down(ch);
#endif
```

init 路径同样分叉：`dac_ll_pad_set_data_source(channel, DAC_DATA_SOURCE_DMA)` +
`dac_ll_pad_power_on(channel)`，循环后 `dac_ll_sync_by_adc(false)` +
`dac_ll_dma_clk_inv(true)`。另在文件头加入受 `__has_include` 保护的
`#include <esp_idf_version.h>`。

### 执行

- 环境：macOS arm64，Docker；镜像 `espressif/idf:v6.1.1`（linux/arm64），容器内 IDF 版本
  `IDF_INIT_VERSION=6.1.1`；编译器 `xtensa-esp32-elf-g++ 15.2.0`，`-std=gnu++26`。
- 工程：`code/` 中的最小 IDF 应用；`components/M5GFX` 为 `b48dce0` 源码，`main` 仅
  `#include "M5GFX.h"` 并实例化 `M5GFX`。
- 命令（等价）：`idf.py set-target esp32 && idf.py build`。
- 未打补丁：在 `lgfx_v1_platforms.cpp` 编译阶段失败，5 条错误与报告一致；日志见
  `evidence/build-unpatched-errors.txt`（完整日志 `evidence/build-unpatched-fail-idf611-esp32.log`）。
- 打补丁：`git apply` 后同一构建 1057 步完成，`Project build complete`，产出
  `m5gfx425.bin` 312,304 字节，
  SHA-256 `553a7476027b1221092685286a9787d738c8cce535873465ed593711bf0ac03f`
  （`evidence/build-patched-pass-idf611-esp32.log`、`evidence/build-artifact.txt`）。
- 补丁基线检查：对 `b48dce04c80d3e3c9874b7ba946c43d672129c28` 执行
  `git apply --check` 通过（`evidence/patch-apply-check.txt`）。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build（未打补丁，v6.1.1/esp32） | `FAIL` | 5 条 `dac_ll_*` 未声明错误，复现报告 |
| build（打补丁，v6.1.1/esp32） | `PASS` | 全量构建完成，产物 312,304 字节，SHA-256 已记录 |
| API 事实与版本边界 | `PASS` | v6.1 与 v6.1.1 头文件逐项对照；master 同为 6.1.1 的新名字 |
| patch 基线可应用 | `PASS` | `git apply --check` 于 `b48dce0` 通过 |
| CVBS 运行（DAC 复合视频） | `NOT RUN` | 无实机，也没有 DAC/CVBS 虚拟模型 |
| hardware validation | `NOT RUN` | 未在 esp32 机型烧录验证 |
| virtual-device validation | `NOT RUN` | Device Service / esp-emulator 无 ESP32 DAC/CVBS 模型 |
| 旧版本回归构建（6.1 / 6.0.2） | `NOT RUN` | `< 6.1.1` 分支代码未变，未重跑 |
| Arduino-ESP32 内核构建 | `NOT RUN` | 本次只验证 ESP-IDF 组件路径 |

## 验证边界

- 结论只到 build 层：补丁使代码可编译、可链接，没有证明 CVBS 输出画面正确。DAC DMA 的
  数据源、时钟反相与 APLL 配置属于运行时行为，需要示波器/视频采集或真实复合视频输入才能判定。
- 未做虚拟设备验证的原因：本机 Device Service 的 esp32 profile（stickc-plus2 等）没有 DAC 或
  CVBS 外设模型，esp-emulator 也没有对应设备；且这是编译期错误，未修复前无法进入运行时。
- IDF 版本判断使用 `ESP_IDF_VERSION >= ESP_IDF_VERSION_VAL(6,1,1)`。已确认 v6.1.1 与当前
  IDF master 都提供新名字；v6.1 仍是旧名字。未逐一验证 6.1.1 之后的所有补丁版本。
- 补丁是建议方案，未提交上游；维护者可能更倾向集中封装一层 DAC LL 兼容宏。

## 风险与回滚

- 无实机、无烧录、无不可逆操作；只在一次性容器和临时工程中构建。
- 补丁对旧 IDF 分支不改变任何代码路径；如上游合并后发现 CVBS 画面异常，回滚该文件即可，
  不涉及其他模块。

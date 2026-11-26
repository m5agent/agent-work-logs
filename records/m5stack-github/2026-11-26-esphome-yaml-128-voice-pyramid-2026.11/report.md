# 报告：Voice Pyramid 灯组件在 ESPHome 2026.11.x 的编译失败

## 1. 问题来源与现象

`m5stack/esphome-yaml#128`（作者 `davidrule1969`，2026-11-26）报告：使用
`examples/voice_assistant/atoms3r-voice-pyramid-satellite.factory.yaml`（或其中引用的
`common/atoms3r-voice-pyramid-satellite.yaml`）在 ESPHome 2026.11.1 下编译失败，同一配置在 2026.10.2 下正常。
首两条致命错误位于 `esphome/components/m5_voice_pyramid_kit/light/`：

```text
m5_voice_pyramid_light.h:29:23: error:
'esphome::light::ESPColorView esphome::m5_voice_pyramid_kit::M5VoicePyramidKitLight::get_view_internal(int32_t) const'
marked 'override', but does not override

m5_voice_pyramid_light.cpp:83:3: error:
could not convert '{ ... }' from '<brace-enclosed initializer list>' to 'esphome::light::ESPColorView'
```

该 YAML 通过 `external_components` 从 `github://m5stack/esphome@feat-voice-pyramid` 拉取
`m5_voice_pyramid_kit`、`aw87559`、`si5351`、`m5_atoms3_voice_ui`，其中灯组件就在该分支上。

## 2. 根因

上游改动：`esphome/esphome#21577`「`[light] Refactor ESPColorView and related types`」，
2026-10-31 合入，2026.11.0 首次随发布带出。该 PR 明确标注 *developer breaking change*：

- `AddressableLight` 不再声明 `virtual ESPColorView get_view_internal(int32_t) const = 0;`，
  改为由 `ESPColorAccessor *accessor_` 提供像素读写；`operator[]`/`get()`/`range()` 都经由 accessor。
- `ESPColorView` 由「六个裸指针字段」改为 `ESPColorView(ESPColorAccessor *, int32_t)`，
  旧的聚合初始化不再可编译。
- 外设组件的迁移方式是提供一个 accessor（core 里有 `RawBufferColorAccessor`、
  `CorrectedBufferColorAccessor`，缓冲区布局用 `ChannelColors{r, g, b, w}` 描述），并在 `setup()`
  里把 `this->accessor_` 指向它。参考 `esphome/components/esp32_rmt_led_strip/led_strip.cpp:136`
  与 `esphome/components/partition/light_partition.h`。
- 官方迁移说明：`https://developers.esphome.io/blog/2026/11/18/addressable-light-now-backed-by-a-color-accessor/`

被测组件（`m5stack/esphome@feat-voice-pyramid`，head `61b5ecbb`，2026-10-23）仍然是旧写法：

- `esphome/components/m5_voice_pyramid_kit/light/m5_voice_pyramid_light.h:29`
  `light::ESPColorView get_view_internal(int32_t index) const override;`
- `esphome/components/m5_voice_pyramid_kit/light/m5_voice_pyramid_light.cpp:78-85`
  `return {led + 2, led + 1, led + 0, nullptr, this->effect_data_ + index, &this->correction_};`

因此 2026.11.x 下必然失败；该分支的时间点也解释了为什么今天仍失败（不是已修复问题的残留报告）。

## 3. 复现方式

最小配置（`code/pyramid-light.yaml`）：只保留 `esp32` + `esp-idf`、`logger`、一条 `i2c` 总线、
`external_components: github://m5stack/esphome@feat-voice-pyramid`（只取 `m5_voice_pyramid_kit`）、
以及 `light: platform: m5_voice_pyramid_kit` 的单通道实例如下。

```bash
# 2026.11.1（失败）
ESPHOME_DATA_DIR=/tmp/esphome-data-2611 esphome compile pyramid-light.yaml
# 2026.10.0（通过，对照）
ESPHOME_DATA_DIR=/tmp/esphome-data-2610b esphome compile pyramid-light.yaml
```

两个 venv 分别安装 2026.11.1 / 2026.10.0，共用已缓存的 ESP-IDF 5.5.6 工具链，
目标板 `esp32-s3-devkitc-1`（ESP32-S3，与 AtomS3R 同 SoC），构建产物不烧录。

## 4. 参考补丁与验证矩阵

`patches/0001-voice-pyramid-2026.11-accessor.patch`（base `61b5ecbb`，`git apply --check` 通过）：

- 头文件：`ESPHOME_VERSION_CODE >= VERSION_CODE(2026, 11, 0)` 时声明
  `light::CorrectedBufferColorAccessor internal_accessor_{};`，否则保留 `get_view_internal` 声明。
- `setup()`：缓冲区分配成功后
  `internal_accessor_ = CorrectedBufferColorAccessor(buf_, effect_data_, ChannelColors{2,1,0}, &correction_);`
  再 `accessor_ = &internal_accessor_;`（`{2,1,0}` 对应原代码 red→byte2 / green→byte1 / blue→byte0 的 BGR 布局）。
- `.cpp`：`get_view_internal()` 定义整体放进 `#if ESPHOME_VERSION_CODE < VERSION_CODE(2026, 11, 0)`。

| 组件 | ESPHome | 结果 | 说明 |
| --- | --- | --- | --- |
| 上游 head（未改） | 2026.11.1 | `FAIL` | 与 issue 完全相同的两条 error |
| 上游 head（未改） | 2026.10.0 | `PASS` | 对照，证明配置本身可用 |
| 参考补丁 | 2026.11.1 | `PASS` | 生成 `firmware.factory.bin` |
| 参考补丁 | 2026.10.0 | `PASS` | 旧路径仍编译，门控生效 |

符号对照（`evidence/symbols.txt`）：

- 2026.11.1 + 补丁：`M5VoicePyramidKitLight::get_view_internal` 消失，出现 5 个
  `light::CorrectedBufferColorAccessor` 符号；
- 2026.10.0 + 补丁：`get_view_internal` 仍在，`CorrectedBufferColorAccessor` 计 0；
- 三个构建目录里生成的 `src/esphome/core/version.h` 分别为 `2026.10.0` / `2026.11.1` / `2026.10.0`，
  说明门控读的是构建期生成的版本头，而不是源码树里 `VERSION_CODE(2099, 12, 0)` 的 stub。

## 5. 虚拟设备尝试（未完成）

为验证 accessor 是否真的接管了像素读写，把「补丁 + `logger: VERY_VERBOSE` + `on_boot`
点亮 `pyramid_rgb1`」的固件（`code/pyramid-light-runtime.yaml`，sha256 `a2e8d178…c45ea`）
导入本机 Device Service，在 `atoms3r` 与 `cores3` 两个 ESP32-S3 profile 上各起一次会话：
三次会话都只输出 ROM 与二级 bootloader 横幅（226 字节）后停住，`atoms3r` 的那次以
`timed out waiting for serial marker 'setup() finished successfully'` 失败
（`evidence/serial-evidence.txt`）。由于应用未跑到 `setup()`，拿不到 core 的
`[VV][light.addressable]` 周期像素转储，因此 accessor 的运行态读回记为 `NOT RUN`。

另需说明的模型边界：Voice Pyramid 的 RGB 控制器是 I2C `0x1A` 的自定义控制器，现役 profile 没有该模型，
即使应用启动成功，`write_channel_rgb()` 的写入也会 NAK，因此该路径本来也无法在虚拟设备上完成闭环。

## 6. 影响面与建议

- 影响面：任何使用 `github://m5stack/esphome@feat-voice-pyramid` 并在 ESPHome 2026.11.x 上编译
  Voice Pyramid 配置的用户都会失败；同分支上若还有别的 `AddressableLight` 子类也需要同样迁移。
- 修复位置在 `m5stack/esphome` 的 `feat-voice-pyramid` 分支（本仓库 YAML 无需改动）。
  若该分支不再维护、组件要迁到 `m5stack/esphome` 主线，迁移同样适用。
- 短期规避：继续使用 ESPHome 2026.10.x。
- 顺带记录：`m5stack/esphome@m5-dev` 上仍有 `m5ioe1`、`m5_unit_extio2` 等旧写法灯组件，
  与本 issue 同源（该仓库已另起 `m5stack_ioe1` 并完成迁移，见 `#127` 评论里的提交
  `8ba135cd5a84fbb385412be05159a8ff03b74c57`）。

## 7. 未覆盖项与风险

- 实机 AtomS3R + Voice Pyramid 的灯珠颜色顺序、亮度、音频与触摸：`NOT RUN`。
- 虚拟设备上的 accessor 读回：`NOT RUN`（应用未启动到 `setup()`，见第 5 节）。
- 完整 `atoms3r-voice-pyramid-satellite.factory.yaml` 全量构建：`NOT RUN`；本次只隔离灯组件，
  其余外部组件（`lp5562` / `aw87559` / `si5351` / `m5_atoms3_voice_ui` / `esphome-audio-stack`）
  在 2026.11.1 下的状态未逐一验证，不排除后续还有第二个错误。
- 参考补丁只证明「可编译」，`ChannelColors{2,1,0}` 与实际控制器寄存器顺序的一致性依赖原代码注释，
  需实机确认颜色通道是否正确。

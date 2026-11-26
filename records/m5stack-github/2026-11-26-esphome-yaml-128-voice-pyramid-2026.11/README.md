# esphome-yaml #128 Voice Pyramid 例程在 ESPHome 2026.11.1 编译失败

- 日期：`2026-11-26`
- 结果：`PARTIAL`（2026.11.1 复现失败、2026.10.0 对照通过、参考补丁在两端均构建通过；实机与虚拟设备运行 `NOT RUN`）
- 工作类型：`issue_triage`
- 问题来源：https://github.com/m5stack/esphome-yaml/issues/128
- 组件来源：`m5stack/esphome @ feat-voice-pyramid` head `61b5ecbbef5b862824f6cec75b6a14b6561a7dca`（2026-10-23）
- 配置来源：`m5stack/esphome-yaml @ main` `bc507b50d818c316fe1e9d60a8f6b971d96952a1`
- 环境：macOS 主机；ESPHome 2026.11.1 与 2026.10.0（各自独立 venv）+ ESP-IDF 5.5.6；本机 Device Service 的 `atoms3r` / `cores3`（QEMU，ESP32-S3）

## 结论

报告的现象在 ESPHome 2026.11.1 上可稳定复现，根因是 ESPHome 2026.11 的开发者级 API 变更，
不是本仓库 YAML 或配置问题：

- 上游 PR `esphome/esphome#21577`（`[light] Refactor ESPColorView and related types`，2026-10-31 合入，
  首个包含该改动的发布为 2026.11.0）把 `AddressableLight` 改为由 `ESPColorAccessor` 支撑：
  `get_view_internal()` 被移除，`ESPColorView` 也不再接受六个裸指针的聚合初始化。
- `m5_voice_pyramid_kit` 的 `M5VoicePyramidKitLight` 仍在实现 `get_view_internal()` 并用
  `{red, green, blue, white, effect_data, correction}` 构造视图，因此在 2026.11.x 上必然编译失败，
  报错与报告中的两条完全一致。
- 该组件分支最后更新于 2026-10-23，早于 2026.11 发布，所以当前 `feat-voice-pyramid` 分支在今天
  （2026-11-26）仍然失败，不是作者环境问题、也不是已经修好的旧问题。
- 迁移方式与 core 的 `esp32_rmt_led_strip`、`light_partition` 一致：在 `setup()` 分配完缓冲区后挂
  `light::CorrectedBufferColorAccessor`（本例缓冲区是 B、G、R 排列，故 `ChannelColors{2, 1, 0}`），
  并设置 `this->accessor_`；用 `ESPHOME_VERSION_CODE` 门控可同时兼容 2026.10。

## 关键证据

构建矩阵（均 `esp32-s3-devkitc-1` + `esp-idf`，只包含 `m5_voice_pyramid_kit` 与一路 addressable light）：

| 组件版本 | ESPHome | 结果 | 产物 sha256（app bin） |
| --- | --- | --- | --- |
| `feat-voice-pyramid` head | 2026.10.0 | `PASS` | `82dabb1a…609fafa` |
| `feat-voice-pyramid` head | 2026.11.1 | `FAIL`（两条报错与 issue 一致） | — |
| 本地参考补丁 | 2026.11.1 | `PASS` | `8095d05f…207f3d5c` |
| 本地参考补丁 | 2026.10.0 | `PASS` | `9bb99718…121e96d42` |

- 失败日志：`evidence/fail-2026.11.1.log`（`…light.h:29:23: error: … marked 'override', but does not override`、
  `…light.cpp:83:3: error: could not convert … to 'esphome::light::ESPColorView'`）
- 符号对照：`evidence/symbols.txt`
  - 2026.10.0（未改）：ELF 保留 `M5VoicePyramidKitLight::get_view_internal(long) const`，无 accessor 符号；
  - 2026.11.1（补丁）：该符号消失，出现 5 个 `light::CorrectedBufferColorAccessor` 符号；
  - 2026.10.0（补丁）：旧符号仍在，说明门控解析的是构建生成的 `version.h`，不是源码树里的 `2099.12.0` stub。
- 参考补丁：`patches/0001-voice-pyramid-2026.11-accessor.patch`，对 base `61b5ecbb` 通过 `git apply --check`。
- 配置：`code/pyramid-light.yaml`（最小复现）、`code/pyramid-light-runtime.yaml`（运行态尝试）。

## 文件

- `report.md`：完整报告、代码位置、验证矩阵、边界
- `run.json`：结构化记录
- `evidence/`：构建摘要、编译日志、符号、固件哈希、虚拟设备串口摘录
- `code/`：最小复现配置与运行态配置
- `patches/`：2026.11 accessor 迁移参考补丁

## 未覆盖项

- 实机 AtomS3R + Voice Pyramid 上的灯珠输出、颜色顺序与音频/触摸：`NOT RUN`（本机无该套硬件）。
- 虚拟设备运行：`NOT RUN`。同一固件在 Device Service 的 `atoms3r`、`cores3` 两个 ESP32-S3 profile
  上只走到 ROM/二级 bootloader 串口横幅（226 字节）就不再输出，因此拿不到 accessor 的像素读回；
  此外 Voice Pyramid 的 RGB 控制器（I2C `0x1A`）本身没有模型，即使启动成功也只会 NAK。
  这是本次验证未完成的实测边界，不代表被测固件在真机上的行为。
- 完整 `atoms3r-voice-pyramid-satellite.factory.yaml` 全量构建：`NOT RUN`（该配置还拉取 `lp5562`、
  `aw87559`、`si5351`、`m5_atoms3_voice_ui`、`esphome-audio-stack` 等外部组件，首个致命错误即本例的灯组件；
  本次只隔离出该组件做最小复现，未逐一验证其余组件在 2026.11.1 下的状态）。

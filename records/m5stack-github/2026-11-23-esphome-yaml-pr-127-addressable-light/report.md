# m5stack/esphome-yaml PR #127 评审报告

## 1. 背景与目标

PR #127（作者 pfefferle）修复 ESPHome 2026.11.0 对 addressable light 的 API 变更：
`AddressableLight::get_view_internal()` 被移除，改为通过 `ESPColorAccessor` 访问像素。
PR 为 `m5ioe1` 与 `extio2` 两个组件加上版本门控，在 2026.11 使用
`CorrectedBufferColorAccessor`，在 2026.10 保留旧 `get_view_internal()`。

目标是确认：

1. 2026.11.0 下两个组件能编译；
2. 2026.10.0 下旧路径仍然编译（作者声称的向后兼容）；
3. 新 accessor 在运行时确实绑定到组件的 `buf_`/`effect_data_`，而不是默认空访问器。

PR 当时状态 OPEN、draft=false、无既有评论；CI 只有 `wecom-digest-forward` 转发任务，
不提供构建验证。评审结论以英文单条评论发布：
https://github.com/m5stack/esphome-yaml/pull/127#issuecomment-7094556591

## 2. 改动审阅

改动位置（PR head `385dc4b`）：

| 文件 | 行 | 内容 |
| --- | --- | --- |
| `components/m5ioe1/light/m5ioe1_light.h` | 32-38 | 2026.11 分支声明 `CorrectedBufferColorAccessor internal_accessor_{nullptr, nullptr, {0,1,2}, &this->correction_}`；否则声明旧 override |
| `components/m5ioe1/light/m5ioe1_light.cpp` | 34-38 | `setup()` 中把 `buf_`/`effect_data_` 填入 accessor 并设置 `this->accessor_` |
| `components/m5ioe1/light/m5ioe1_light.cpp` | 70-82 | 旧 `get_view_internal()` 用 `ESPHOME_VERSION_CODE < 2026.11.0` 包住 |
| `components/extio2/light/extio2_light.h` | 54-60 | 同上，`internal_accessor_` + 版本门控 |
| `components/extio2/light/extio2_light.cpp` | 120-124 | `setup()` 中绑定 accessor |
| `components/extio2/light/extio2_light.cpp` | 161-176 | 旧 `get_view_internal()` 版本门控 |
| 两个 `.h` | 头部 | 新增 `#include "esphome/core/version.h"` |

对照 ESPHome 2026.11.0 core：

- `esphome/components/light/addressable_light.h:126` 的 `accessor_{&NullColorAccessor::instance}`
  是基类唯一的访问入口；`operator[]`、`get()`、`range()` 都通过它。
- `esphome/components/light/esp_color_view.h:132-169` 的 `CorrectedBufferColorAccessor`
  构造参数为 `(uint8_t *color_data, uint8_t *effect_data, ChannelColors, const ESPColorCorrection *)`，
  与 PR 的初始化列表一致。
- `ChannelColors{0,1,2}` 表示 RGB 三字节紧密布局（`w=NO_WHITE`、`bytes_per_led()==3`），
  与旧 `ESPColorView(&buf[pos], &buf[pos+1], &buf[pos+2], nullptr, &effect_data[index], &correction_)`
  的语义一致：`get()` 做 color uncorrect，`set()` 做 color correct，effect data 读写一致。
- core 的 `esp32_rmt_led_strip`、`rp2040_pio_led_strip`、`beken_spi_led_strip` 均使用同一
  `internal_accessor_{nullptr, nullptr, {0,1,2}, &this->correction_}` + `this->accessor_ = ...`
  模式；`m5stack_8angle`（同为 I2C 扩展器驱动灯条）也在 2026.11 采用该 accessor。

未发现越界修改、公共 API 变化或与 PR 描述不一致的代码。

## 3. 验证环境与方法

- 主机：macOS（Apple Silicon），Python 3.13 venv。
- ESPHome 2026.11.0、2026.10.0 分别从公开 PyPI 安装；ESP-IDF 5.5.6 由 ESPHome 管理。
- 板型：`esp32dev`（ESP32，4 MB flash，`framework: esp-idf`）。
- 组件：本地 `external_components` 指向 PR head 的 `components/`，同时启用 `m5ioe1` 与
  `extio2` hub 及各自的 addressable light（`code/pr127.yaml`）。
- 构建命令：`esphome config pr127.yaml`、`esphome compile pr127.yaml`（两个版本各一次）。
- 运行时：本机 Device Service，`atom-echo`（ESP32，QEMU，`runtime=qemu`）；上传
  `firmware.factory.bin`，组合为 4 MiB merged image，创建 300 s 会话并采集串口。

运行时配置在 `code/pr127-runtime.yaml`：VERY_VERBOSE 日志，`on_boot` 把两灯分别设为
红/绿，用于让 core 的 `AddressableLight::call_setup()` 5 s 周期像素 dump 走新 accessor。

## 4. 结果

### 4.1 构建

| 版本 | 结果 | 产物 sha256 |
| --- | --- | --- |
| ESPHome 2026.11.0 | PASS，`Successfully compiled program.` | `d063c9ab956eb414bb5df74002067afd984cbffa7a1c9fd933184c6b39b772c1` |
| ESPHome 2026.10.0 | PASS，`Successfully compiled program.` | `78847daabbb4ed216dbba26281a79c02428b410fbb16ff9c127b2cc049306192` |

版本门控的实际效果用 ELF 符号核对：

- 2026.10.0 ELF：存在 `esphome::extio2::EXTIO2AddressableLight::get_view_internal(long) const`
  与 `esphome::m5ioe1::M5IOE1AddressableLight::get_view_internal(long) const`。
- 2026.11.0 ELF：上述符号 0 个。

两次构建的 `src/esphome/core/version.h` 分别为 `VERSION_CODE(2026, 10, 0)` 与
`VERSION_CODE(2026, 11, 0)`，证明判断使用的是构建生成头而不是源码树 stub
（stub 为 `VERSION_CODE(2099, 12, 0)`）。

2026.11 构建中唯一的告警是 `extio2_light.cpp` `dump_config()` 的 `%d` 对 `int32_t`
（既有代码，非本 PR 引入）。

### 4.2 虚拟设备运行

- 会话 `27bf5e12a00047d1a61ee4e548c77479`，profile `atom-echo`，`runtime=qemu`，已正常 stop。
- 串口显示 `ESPHome version 2026.11.0`、`setup() finished successfully!`。
- 两轮完整像素 dump（去掉 ANSI）：

```
Addressable Light 'M5IOE1 Strip' (effect_active=NO)
  [ 0] Color: R=255 G=  0 B=  0 W=  0
  ... (4 pixels, all R=255)
Addressable Light 'EXTIO2 Strip' (effect_active=NO)
  [ 0] Color: R=  0 G=255 B=  0 W=  0
  ... (4 pixels, all G=255)
```

这两组值来自 `on_boot` 的 `light.turn_on`，经新 accessor 的 `set()` 写入 `buf_`，再由 core
的 dump 通过 `get()` 读回；若 `accessor_` 仍指向 `NullColorAccessor`，读回值会是 0。

同时串口出现 `TX to 6F failed: not acked` / `TX to 45 failed: not acked`，两个 hub 被标记
failed。这是 `atom-echo` profile 没有 AW9523/EXTIO2 控制器模型导致，属预期的板级模型缺口，
不影响 light 组件自身的 buffer/accessor 初始化路径。

## 5. 兼容性与影响面

- 2026.11 路径只替换像素访问机制，`write_state()` 仍直接读取 `buf_`（RGB888，m5ioe1 再转
  RGB565），写入范围与旧实现相同。
- 灯珠数量、effect data 分配大小、RGB 通道顺序、颜色校正语义均未改变。
- 2026.10 代码路径保持原样，由构建实测确认仍可编译。
- 组件被 `.h` 新增的 `esphome/core/version.h` 只用于版本判断，无额外依赖。

## 6. 后续事项（不阻塞本 PR）

1. `common/stackchan-voice-assistant-base.yaml` 的 `external_components` 从
   `github://m5stack/esphome@m5-dev` 取 `m5ioe1`，因此 StackChan 配置仍会在 2026.11 下编译失败，
   直到 `m5stack/esphome` 里的同一组件完成迁移（作者已在正文说明并愿开第二个 PR）。
2. `examples/kit/stackchan-bsp.factory.yaml` 使用 `github://m5stack/esphome-yaml/components`，
   本 PR 合并后会获得修复。
3. README 的 ESPHome 版本徽章仍为 2026.10.0，如仓库把该徽章当作支持版本声明，可一并更新。

## 7. 边界与回滚

- 实机 M5IOE1/EXTIO2 的 LED 输出、颜色顺序、亮度与灯珠光学：`NOT RUN`。
- 扩展器 I2C 总线上的真实写入载荷：`NOT RUN`（虚拟板未建模对应控制器）。
- 效果动画（rainbow/twinkle/lambda）逐帧行为：`NOT RUN`，仅验证了 accessor 的静态 set/get。
- 无代码改动需要回滚；若上游 API 再变，删除 2026.11 分支即可回到旧实现。

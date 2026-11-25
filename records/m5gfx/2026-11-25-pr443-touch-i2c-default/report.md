# M5GFX #443 报告：触摸 I2C 默认时钟 1 MHz → 400 kHz

## 1. 任务背景

PR #443 把 `lgfx::ITouch::config_t::freq` 的默认值从 `1000000` 改为 `400000`。作者理由：
多数触摸控制器走 I2C，Fast-mode 400 kHz 是数据手册常见上限；未显式设置 `cfg.freq` 的
I2C 触摸驱动此前以 1 MHz 运行。PR 正文还列了 SPI 触摸驱动的行为变化和软 I2C 变慢等副作用。

评审目标：确认默认值改动的正确性、对 M5GFX 板级自动识别路径的影响面、以及是否存在
依赖旧默认值的代码/文档/测试。

## 2. 代码事实

### 2.1 差异范围

`git diff e7cae68..2c6b0f0` 只有 `src/lgfx/v1/Touch.hpp` 一个文件，+3/-1：
基地版 `:43` 为 `uint32_t freq = 1000000;`，PR `:45` 为 `uint32_t freq = 400000;` 并加两行注释。

### 2.2 哪些驱动吃这个默认值

M5GFX 现有触摸驱动（PR head）：

| 驱动 | 构造器是否设 freq | 位置 |
| --- | --- | --- |
| `Touch_CST3530` / `CST816S` / `CST226` / `CST9217` | 否 | `Touch_CSTxxx.hpp:37/:64/:113/:169` |
| `Touch_CHSC6540` | 否 | `Touch_CHSC6540.hpp:28` |
| `Touch_GT911` | 否 | `Touch_GT911.hpp:28` |
| `Touch_ST7123`（P4） | 否 | `platforms/esp32p4/Touch_ST7123.hpp:28` |
| `Touch_FT5x06` | 是，400 kHz | `Touch_FT5x06.hpp:37` |
| `Touch_sdl` | 主机端，无 I2C | `platforms/sdl/...` |

`grep '_cfg.freq' src/lgfx/v1/touch/` 只命中 FT5x06 一处，作者“这些驱动没设时钟”的说法成立。
`config_t` 是整体拷贝（`Touch.hpp:81-82`），所以用户常见的
`auto cfg = touch.config(); ... touch.config(cfg);` 会拿到构造器里的默认值。

### 2.3 板级自动识别路径不变

- `i2c_touch_desc_t` 构造器的 `freq` 默认就是 400000（`construct_common.inl:250`）。
- `apply_i2c_touch_desc()` 无“保留原值”语义，总是 `cfg.freq = desc.freq`
  （`construct_common.inl:426-441`）；`make_i2c_touch()` 全部经它（`:445-447`）。
- 所有 `out.touch.reset(...)` 触摸对象都走 `make_i2c_touch<...>()`，唯一例外是 CoreS3 的
  `make_default_part<Touch_M5StackCoreS3>()`（`esp32s3_construct.inl:736`），而
  `Touch_M5StackCoreS3` 自己写 `_cfg.freq = i2c_freq`（`M5GFX.cpp:503`，`i2c_freq=400000`，`:446`）。

结论：板级路径在 PR 前后都是 400 kHz，这一点由虚拟设备对照实测确认（两版
`board_touch ... freq=400000`）。因此 PR 的实际行为变化只落在“第三方自定义板/自己拼
`config_t` 且不设 `freq`”的用法上，与作者在正文里的 “Behavior change” 描述一致。

### 2.4 软 I2C 副作用

`soft_i2c.inl:118-124`：

```
ctx.half_us = (freq >= 500000) ? 0 : (500000 + freq - 1) / freq;
```

400 kHz 时每半周期等 2 µs，1 MHz 时不等。也就是说旧值在软 I2C 上并不是真的 1 MHz 总线，
而是“跳过半周期等待”；改成 400 kHz 后软 I2C 触摸读会变慢。M5GFX 内置板没有走软 I2C 的
触摸（唯一负端口是 `detection_i2c_port = -1`，`M5GFX.cpp:136`），只有用户自定义
`i2c_port < 0` 时才会中招。

### 2.5 描述与仓库范围不一致

PR 正文列出的 CHSC6x、NS2009、TT21xxx、GSLx680、XPT2046、RA8875、STMPE610 在
m5stack/M5GFX 中都不存在；这些是 LovyanGFX 的驱动。作者同时在 lovyan03/LovyanGFX#1019
提交了同名改动，正文应是从那里复用的。对 M5GFX 的代码没有影响，但“SPI 触摸驱动行为变化”
一节在本仓库不适用，建议按实际范围修描述。

未发现示例、文档或 host 测试依赖旧的 1 MHz 默认（`grep 1000000` 仅命中无关的 CPU 频率字段）。

## 3. 验证

### 3.1 构建

两棵只读树（PR head / develop）用同一个探针 `main.cpp` 替换
`examples/Test/build_test/main/main.cpp`，ESP-IDF v6.1、`esp32s3`、8 MB flash、
8 MB octal PSRAM 构建，esptool 合并为 8 MB 头镜像。探针：
读 `ITouch::config_t{}.freq`；`M5GFX::init()` 后打印板级触摸 config；
再用 `Touch_CST816S` 的 `config()` 复制默认值、按 StopWatch 的 port/pins 配置并 `init()`，
轮询 `getTouchRaw()`，同时在屏上画背景、标签和触摸点标记。

### 3.2 虚拟设备

Device Service `stopwatch` profile（`qemu-esp32s3` / `m5stopwatch`，CO5300 466×466，
`peripheral_status=simulated`，warnings 为空）。两版各建一个会话，同一注入：

```
POST /api/v1/sessions/{id}/input  {"kind":"touch","x":120,"y":120,"settle_seconds":0.3}
```

| 观测 | PR | base |
| --- | --- | --- |
| `default_config_freq` | 400000 | 1000000 |
| `driver_default_freq` | 400000 | 1000000 |
| `applied_freq` | 400000 | 1000000 |
| `board_touch ... freq` | 400000 | 400000 |
| `touch_init` | 1 | 1 |
| 注入后 `raw` | `n=1 x=120 y=120` | `n=1 x=120 y=120` |
| 466×466 截图 sha256 | `d2a742c8…1a8a2` | `d2a742c8…1a8a2` |

两版画面逐字节相同：深色底 + 注入点 `(120,120)` 的 9×9 绿色标记。左上角文字标签在抓帧里
被裁切（面板/抓帧原点差 6 px），不作为证据使用。

### 3.3 host 与 CI

- `bash test/board_detect/run.sh`：34 个 C++ 测试程序全通过。
- 上游检查 38/38 pass，全部是构建类 job（Arduino 2.0.17–4.0.0、IDF 5.1.6/5.4.3/6.0.2 等）。

## 4. 兼容性与风险

- API/ABI 无变化，只是默认值。
- 已显式设置 `cfg.freq` 的代码不变；板级自动识别不变。
- 潜在影响：第三方自定义板若依赖旧的 1 MHz 默认（例如长排线/特定控制器），升级后会被
  降到 400 kHz；这是作者声明的有意行为变化，可按需要在自定义 `config_t` 里显式设回。
- 若需回滚：把 `Touch.hpp` 的默认值改回 1 MHz 即可，无其它耦合。

## 5. 未覆盖项与边界

- hardware validation `NOT RUN`：本机无 StopWatch / GT911 / CHSC6540 实物。
- 真实 SCL 频率未测量：QEMU 的 I2C 路径按控制器命令+FIFO 解码，不建模 SCL 周期；
  1 MHz 与 400 kHz 配置下同一读序列都成功，不能据此证明电气时序。
- 只验证 CST816S（StopWatch 上是 CST820）；GT911、CHSC6540、CST9217、ST7123 未跑。
- 软 I2C 的 2 µs 半周期等待未做时序测量，也未做长稳/热复位/连续触摸。

## 6. 评审结论

方向正确、实现最小、板级路径零变化，未发现阻塞合并的问题。唯一建议是修正 PR 描述中
不属于本仓库的驱动清单；不要求改代码。

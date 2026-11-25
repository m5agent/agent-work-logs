# M5GFX #443：触摸 I2C 默认时钟改为 400 kHz

- 日期：`2026-11-25`
- 结果：`PARTIAL`（virtual-device validation + code-level verification；真实 SCL 频率与真机 `NOT RUN`）
- 工作类型：`pr-review`
- 问题来源：[m5stack/M5GFX#443](https://github.com/m5stack/M5GFX/pull/443)，作者 `ainyan03`，英文，OPEN；
  评审前 comments / reviews 均为 0
- 源码版本：`m5stack/M5GFX` PR head `2c6b0f01090bdfc8b3007f652dc9510cf797c37b`
  （base `e7cae681dd5ec6707b5c174a6b75cb5061c3f3d9` = develop tip）
- 环境：macOS arm64；ESP-IDF v6.1 本地构建 ESP32-S3；本机 Device Service 的 `stopwatch`
  profile（QEMU `m5stopwatch`，CO5300 466×466，`simulated`，触摸为 CST820 @0x15）

## 结论

改动本身正确，未发现阻塞合并的问题：`ITouch::config_t::freq` 的默认值由 1 MHz 改为 400 kHz，
与常见触摸控制器 I2C Fast-mode 上限一致；M5GFX 的板级自动识别路径显式给每个 I2C 触摸写入时钟
（desc 默认即 400 kHz），所以该 PR 不改变任何已支持机型的运行时行为，只影响第三方代码里
“复制驱动默认 config 后不设 freq”的自定义板写法。

虚拟 StopWatch 上以同一探针固件对照：PR 构建读到默认 400000、base 读到 1000000；两版的
板级触摸时钟都是 400000；CST816S 在两种默认值下 `init()` 均成功、注入 `120,120` 均读到
`x=120 y=120`，466×466 画面逐字节相同。host 测试 34/34、上游 CI 38/38 通过。

PR 描述里的驱动清单（CHSC6x、NS2009、TT21xxx、GSLx680、XPT2046、RA8875、STMPE610）属于
LovyanGFX（同一改动为 lovyanGFX#1019），在本仓库不存在；建议按 M5GFX 的实际范围修描述，
不影响代码。

## 关键证据

- 构建：ESP-IDF v6.1 / `esp32s3` / 8 MB flash + 8 MB octal PSRAM；两棵树同一 `main.cpp` 探针。
  PR app `f4c51930…`、merged `1461feae…`；base app `8bb6e837…`、merged `feee9a03…`。
- 虚拟设备：Device Service `stopwatch`（QEMU），PR 会话 `f1079a8812e74fd0953ad45d760bb325`、
  base 会话 `b89c262aa75249b38222591c58195129`；同一注入 `{"kind":"touch","x":120,"y":120}`。
- 串口：PR `default_config_freq=400000` / `driver_default_freq=400000`；
  base `1000000` / `1000000`；两版 `board_touch ... freq=400000`、`touch_init=1`、
  `raw n=1 x=120 y=120`。
- 画面：PR 与 base 的 466×466 PNG sha256 均为
  `d2a742c83cebbf2bdc4b6400dd5a170f43296e9aaf65bd07ecee9f200ac1a8a2`。
- 代码事实：`Touch.hpp:45`、`construct_common.inl:250/:426-441`、`soft_i2c.inl:123`。
- host：`bash test/board_detect/run.sh` → 34/34 `passed`。

## 文件

- `report.md`：完整报告（影响面、代码路径、验证过程、边界）
- `run.json`：结构化记录
- `evidence/pr443.diff`：PR 完整差异
- `evidence/code-facts.txt`：行号级代码事实与驱动清单
- `evidence/build-info.txt`：构建、产物、会话与串口/画面关键值
- `evidence/serial-pr.txt`、`evidence/serial-base.txt`：两版完整串口
- `evidence/frame-pr.png`、`evidence/frame-base.png`：466×466 截图（同一 SHA256）
- `evidence/host-tests-pr.txt`：board_detect host 测试输出
- `evidence/harness-main.cpp`：两棵树共用的探针 `main.cpp`
- `evidence/ci-status.txt`：上游 38 项检查
- `evidence/device-profile.json`：`stopwatch` profile（已去设备码）
- `evidence/environment.txt`：工具链、flash/PSRAM 配置与 I2C 模型边界
- `evidence/pr-metadata.json`：PR 元数据

## 未覆盖项

- hardware validation：`NOT RUN`。本机没有 StopWatch / GT911 / CHSC6540 等实物。
- 400 kHz 的真实 SCL 频率未测量：QEMU 的 I2C 模型按事务解码，不建模 SCL 周期；
  记录中的频率是驱动配置值，不是示波器/逻辑分析仪测量。
- 仅跑 CST816S（StopWatch 的 CST820）；GT911、CHSC6540、CST9217、ST7123 未运行。
- 软 I2C 变慢（`half_us` 2 µs）未做时序测量；M5GFX 内置板触摸均走硬件 I2C。
- 只做单次上电启动与单次点击，未做长稳、热复位或连续触摸。

# esphome-yaml #127 ESPHome 2026.11 addressable light 兼容性评审

- 日期：`2026-11-23`
- 结果：`PARTIAL`（2026.11/2026.10 构建通过；虚拟设备启动与像素读回通过；实机与真实 LED 输出 `NOT RUN`）
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/esphome-yaml/pull/127
- 源码版本：`m5stack/esphome-yaml @ 385dc4ba8d87b48c87459aa77b98ab2d493683d0`（PR head），base `main @ bc507b50d818c316fe1e9d60a8f6b971d96952a1`
- 公开评论：https://github.com/m5stack/esphome-yaml/pull/127#issuecomment-7094556591
- 环境：macOS 主机；ESPHome 2026.11.0 与 2026.10.0（各自独立 venv）+ ESP-IDF 5.5.6；本机 Device Service 的 QEMU `atom-echo`（ESP32，`partial`/无显示）

## 结论

PR 的版本门控写法正确，兼容 2026.11 与 2026.10 两个 API：

- 2026.11.0 下 `m5ioe1` 与 `extio2` 两个 addressable light 均编译通过，ELF 中已无
  `get_view_internal` 符号；新路径与 core 的 `esp32_rmt_led_strip` / `m5stack_8angle` 使用同一
  `CorrectedBufferColorAccessor{nullptr, nullptr, {0,1,2}, &correction_}` 模式，RGB888 缓冲区布局
  与旧 6 指针 `ESPColorView` 等价。
- 2026.10.0 下同一 PR head 也编译通过，ELF 中仍保留两个 `get_view_internal` 符号，说明
  `ESPHOME_VERSION_CODE` 判断读取的是构建生成的 `version.h`（2026.10.0），不是源码树里
  `VERSION_CODE(2099,12,0)` 的静态分析 stub。
- 虚拟 ESP32 上以 2026.11.0 固件启动成功；core 的 `AddressableLight` VERY_VERBOSE 周期读回
  显示 M5IOE1 灯条 R=255、EXTIO2 灯条 G=255，说明新 accessor 已正确绑定 `buf_`/`effect_data_`，
  不是默认的 `NullColorAccessor`。

未覆盖：没有 M5IOE1/EXTIO2 实机；本机 ESP32 虚拟设备没有 AW9523/EXTIO2 控制器模型，
I2C 0x6F/0x45 均 NAK，因此真实扩展器总线上的 LED 载荷与灯珠光学行为 `NOT RUN`。

## 关键证据

- 构建：`evidence/build-summary.txt`
  - 2026.11.0 `pr127-light.bin` sha256 `d063c9ab...b772c1`
  - 2026.10.0 `pr127-light.bin` sha256 `78847daa...306192`
- 符号对照：`evidence/symbols.txt`（2026.10 有 `get_view_internal`，2026.11 为 0）
- 虚拟设备串口：`evidence/serial-evidence.txt`
  - `ESPHome version 2026.11.0`、`setup() finished successfully!`
  - 两轮完整像素 dump：M5IOE1 `R=255 G=0 B=0`，EXTIO2 `R=0 G=255 B=0`
  - I2C `TX to 6F/45 failed: not acked`（板级模型缺口，非本 PR 回归）
- 会话与产物哈希：`evidence/session-summary.json`、`evidence/firmware-hashes.txt`

## 文件

- `report.md`：完整报告、代码位置、验证矩阵与边界
- `run.json`：结构化记录
- `evidence/`：构建摘要、串口摘录、符号与哈希、会话摘要
- `code/`：复现用最小 ESPHome 配置（`<repo>/components` 为本地 checkout 占位符）

## 未覆盖项

- 实体 M5IOE1 / EXTIO2 上的 LED 输出与颜色顺序：`NOT RUN`（作者亦说明无 EXTIO2 硬件）。
- 扩展器 I2C 写入载荷：`NOT RUN`（虚拟 ESP32 profile 未建模 AW9523/EXTIO2 控制器）。
- 效果动画的逐帧行为：`NOT RUN`（仅验证了 set/get 与静态像素读回）。
- 本仓库 `common/stackchan-voice-assistant-base.yaml` 仍从 `m5stack/esphome@m5-dev` 拉取
  `m5ioe1`，该配置不会因本 PR 自动修复；需要作者提到的第二个 PR。

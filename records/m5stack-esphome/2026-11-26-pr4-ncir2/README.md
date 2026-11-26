# m5stack/esphome#4 Unit NCIR2 组件新增评审

- 日期：`2026-11-26`
- 结果：`REVIEW`
- 工作类型：`pr_review`
- 问题来源：https://github.com/m5stack/esphome/pull/4
- 源码版本：`m5stack/esphome @ 269124e77bbcd2a128f799ed5fcb31e8a1fbc5de`（PR head），base `m5-dev @ 6c84e04afe0985a73c705094f88b4f773ed4b6e9`
- 环境：macOS arm64；CPython 3.13 + 仓库 requirements（ESPHome 2026.11.0-dev）；ESP-IDF 5.5.6；本机 Device Service 1.102.0（`atoms3r` profile + NCIR2 Unit 模型，`cores3` profile 无 Unit）

## 结论

PR #4 是 #2 的 NCIR2 子集：`m5_unit_ncir2.cpp/.h/__init__.py` 与 #2 head 的 blob SHA 完全相同，
组件与测试目录无差异。寄存器映射与厂商库、Unit 内部固件一致；host 测试 20 项与 3 项评审探针全部通过，
esp32-idf 组件构建和 CoreS3/AtomS3R 完整编译通过。本轮首次在 AtomS3R 虚拟设备上挂接 NCIR2 Unit 模型，
实测目标温度 32.00/45.00/-20.50 °C、芯片温度 25.00/30.25 °C、按键 1/0、蜂鸣器开关和 RGB LED 均按组件路径工作。

仍需处理 3 点：`setup()` 首次通信失败即永久 FAILED（NCIR2 内部固件约 500 ms 后才起 I2C）；YAML 告警/发射率
只写寄存器、不发送 `0x80` 保存；告警温度上限 380 °C 超出寄存器 int16 ±327.67 °C 编码范围。无阻塞性协议问题。

## 关键证据

- 代码身份：#2 与 #4 的 NCIR2 组件三个核心文件 blob SHA 相同（见 `evidence/01-source-identity.txt`）。
- host 测试：23 项通过（20 项组件测试 + 3 项评审探针）。
- 构建：`test_build_components.py -c m5_unit_ncir2 -t esp32-idf` 1 passed；CoreS3 与 AtomS3R 完整编译成功。
- 虚拟设备（AtomS3R + NCIR2 Unit，`custom` 端口，SDA=GPIO2/SCL=GPIO1）：总线扫描到 `0x5A`，固件版本 1，
  传感器读数与注入值逐项一致；`switch.turn_on` 后 `buzzer-on=true`，`light.turn_on` 蓝色后 `rgb-led=255`。
- 虚拟设备（CoreS3，无 Unit）：`m5_unit_ncir2 was marked as failed`，之后无重试。
- 探针：YAML 设置写入 `0x22` 但 `0x80=0`；Unit 稍后上线仍保持 FAILED；380 °C 写入为 `0x9470`（-275.36 °C）。

## 文件

- `report.md`：完整报告
- `run.json`：结构化记录
- `evidence/`：串口、Unit 状态、构建与探针输出、配置
- `code/`：评审探针源码与两份可重建配置

## 未覆盖项

- 无实体 NCIR2：hardware validation NOT RUN。
- NCIR2 Unit 模型不实现 STM32 告警状态机，阈值告警、告警灯/告警声的自主行为 NOT RUN。
- Unit 内部 flash 掉电保持、PaHub（`tca9548a` 未建模）路径、真实光学/发射率物理 NOT RUN。
- 模型只在 `atoms3r` 上准入，`cores3` 无 NCIR2 控制器接线，故功能验证使用 AtomS3R。

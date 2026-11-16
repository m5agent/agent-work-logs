# 硬件与虚拟设备边界（2026-11-17）

## 内部硬件测试中心（只读清单，已脱敏）

只读 `overview` / `nodes` 的结果：5 个槽位，3 个在线空闲。

| 槽位（名称保留） | 报告芯片 | 在线 | 状态 |
| --- | --- | --- | --- |
| matrix | ESP32 | 是 | idle |
| corep4 | 报告值为 ESP32，夹具为 ESP32-P4 | 是 | idle |
| sticks3 | ESP32-S3 | 否 | offline |
| stopwatch | 未报告 | 是 | idle |
| 未分配设备 | 未报告 | 否 | offline |

- 没有 ESP32-C5，也没有 UnitNFC（ST25R3916）。
- 该缺陷需要“主机 RTS 硬复位 + 真实从机在一次 read 中途保持 SDA”的状态；测试中心没有可接
  UnitNFC 的 C5 夹具，替代板也没有可用的中途 read 从机。
- 结论：hardware validation = `NOT RUN`（不是未尝试，而是没有匹配硬件）。

## Device Service（虚拟设备）

- `/api/v1/devices` 返回 36 个 profile：ESP32、S3、C6、P4 与 linux-arm64；**没有 ESP32-C5**。
- `esp-emulator` 的 `devices/` 目录只有 `esp32-lx6`、`esp32-s3`、`esp32-c6`、`esp32-p4`、
  `linux-arm64`，没有 `esp32-c5`。
- 即使有 C5 机器，本缺陷还依赖两点未建模的物理状态：
  1. RTS 硬复位后 LP I2C 控制器与 LP 焊盘连接在复位后保留；
  2. 外部 ST25R3916 在字节中途继续驱动 SDA（并有自己的位时序）。
- 结论：virtual-device validation = `NOT RUN`。

## 本机

- macOS；clang C++11 可用，可运行 M5GFX 自带的 `test/board_detect/run.sh`。
- 无 ESP-IDF / Arduino-ESP32 工具链，未构建 C5 固件。

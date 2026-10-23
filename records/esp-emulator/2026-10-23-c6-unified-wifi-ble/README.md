# ESP Emulator ESP32-C6 单 guest WiFi + BLE

- 日期：`2026-10-23`
- 结果：`PASS`（虚拟设备验证）
- 工作类型：`code_change`
- 源码版本：`m5agent/m5stack-esp-emulator @ 42edb77364eb609bd11a41887153647d75dd328b`
- 环境：macOS Apple Silicon、QEMU ESP32-C6、官方 UIFlow2 v2.5.3、Bumble、QEMU SLiRP

## 结论

NanoC6 与 Nesso N1 现在都能在同一个 QEMU ESP32-C6 guest 内同时运行板级
外设、WiFi DHCP/HTTP 和 UART1 HCI BLE。两台设备均通过独立 runner 和单个
Device Service lease。NanoC6 完成独立公网探针；Nesso N1 与 StickS3 的
统一镜像也分别在单个 guest 内完成 `example.com` DNS、IPv4 公网 HTTP、
板级外设和外部 Bumble GATT。

## 关键证据

- QEMU C6 WiFi 完成 scan、Authentication、Association、DHCP、DNS、TCP/HTTP；
- NanoC6 同 guest 通过 RGB/WS2812、蓝色 LED、按键、IR、WiFi 和 BLE；
- Nesso N1 同 guest 通过显示/触摸、PI4IOE、电源遥测、BMI270、SX1262、
  IR、蜂鸣器、公网 DNS/HTTP 和 BLE；
- StickS3 同 guest 通过显示、M5PM1、BMI270、音频、按键、公网 DNS/HTTP
  和 BLE，并由一个 `runtime=qemu-unified` Device Service lease 重测；
- 外部 Bumble peer 完成 NUS GATT discovery、subscribe、write、notification；
- 平台测试 173/173、runtime coverage、peripheral catalog 和 67/67 外设
  全矩阵通过；两个 QEMU patch 均通过 reverse-apply 检查。

## 文件

- `report.md`：根因、修复和验证边界
- `run.json`：结构化结果
- `evidence/`：NanoC6、Nesso N1、StickS3、Device Service、公网和全矩阵摘要
- `patches/`：最小 QEMU WiFi 补丁

## 未覆盖项

真机、RF/PHY/天线、电气测量、WPA2/WPA3、公网 TLS、原生 C6 Bluetooth
controller 和任意公网服务的稳定性未验证。Tab5 和 CardputerZero 不在本次
范围内。

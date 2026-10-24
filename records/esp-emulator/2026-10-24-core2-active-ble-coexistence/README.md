# Core2 active BLE + WiFi/公网两分钟共存

- 日期：`2026-10-24`
- 结果：`PASS`（virtual-device active BLE hold）
- 工作类型：`code_and_validation`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`4e055979c908d40d6c2ca31b78f3711599e90919`
- 基线版本：`5b686a976e679af2638e5b65f83c75e143582977`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40064909368>
- 环境：macOS Apple Silicon；Python 3；QEMU Core2；Bumble GATT peer；Device Service

## 结论

Core2 `core2-native-hci` 新增 `network.ble_linger_seconds`（0–600 秒）：

- GATT 首次 write/notify/ACK 完成后，外部 BLE peer 可继续连接；
- 2 个独立 `/api/v1` lease 在 WiFi、公网 DNS/HTTP 和 BLE 同时 active 时各
  hold 120 秒；
- `2/2 PASS`；
- 每轮 47/47 HLI posts/consumed、38 events、9 ACLs、`hli-errors=0`；
- HLI/meta queue、TX queue 和 `last-error` 均为 0；
- hold 完成时 `peer-closed=0`，不是“peer 已关闭后空跑”；
- `gdb_bridge=false`。

API contract 从 `1.19.0` 升到 `1.20.0`。

## 边界

- 仍是 QEMU virtual-device validation；
- 不证明物理 cache/PSRAM 时序、bit-exact ESP32 BT controller/baseband 或 RF；
- 同 guest 重复 GATT reconnect、多小时 coexistence/soak 和真机仍 `NOT RUN`；
- active BLE 由 external Bumble peer 提供，不是物理 S3/Core2 射频。

## 文件

- `report.md`：实现、执行和验证；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：汇总证据；
- `patches/`、`code/`：不适用，代码与 evidence 在源码仓库。

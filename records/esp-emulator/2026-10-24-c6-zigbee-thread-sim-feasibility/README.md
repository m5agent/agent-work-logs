# ESP32-C6 Zigbee `thread-sim` 可行性

- 日期：`2026-10-24`
- 结果：`PARTIAL`
- 工作类型：`runtime_model_gap`
- 源码提交：`m5agent/m5stack-esp-emulator @ 321a2aa0c364c7c8e0fad2f926c236895faa8e52`
- 环境：macOS Apple Silicon；`esp-emu 0.50.0`；ESP-IDF `v5.5.4`；ESP32-C6

## 结论

`esp-emu --thread-sim` 能在两个 C6 实例之间转发真实 802.15.4 帧。
源码构建的 ESP-IDF `HA_on_off_switch` 和 `HA_on_off_light` 分别完成了
协调器组网和 light steering 启动，但 `Joined network` 和 On/Off 命令没有
完成。

因此 `RUNTIME-02` 继续为 `OPEN`：

- radio 路径不再是“完全没有数据面”；
- commissioning/MAC ACK 语义尚未闭环；
- 公开 M5Burner Zigbee bin 的 ELF SHA 没有匹配文件，不能用 `thread-sim`
  直接验证该公开样本；
- QEMU C6 仍没有 802.15.4/Zigbee controller 模型。

## 关键证据

- switch→light：21 帧、685 bytes；
- light→switch：17 帧、198 bytes；
- `switch_formed_network=true`；
- `light_started_steering=true`；
- `light_joined_network=false`；
- `light_received_on_off=false`。

## 文件

- `report.md`：方法、构建、观测、问题和下一步
- `run.json`：机器可读记录
- `evidence/feasibility.summary.json`：帧计数、artifact hash 和 marker

## 未覆盖项

- 没有把该 `PARTIAL` 结果写成 Zigbee 或固件 PASS/FAIL；
- 没有验证公开 M5Burner Zigbee 样本；
- 没有验证 WiFi/BLE/Zigbee coexistence；
- 没有物理 RF、功耗或真机验证。

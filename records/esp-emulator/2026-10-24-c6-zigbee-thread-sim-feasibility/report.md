# ESP32-C6 Zigbee `thread-sim` 可行性报告

## 背景

`RUNTIME-02` 之前只有 QEMU C6 Zigbee 固件在 `Zigbee_main` 触发 task
watchdog 的负向证据，无法区分固件问题、controller 缺失和 MAC 语义缺失。

本轮改为直接验证 `esp-emu 0.50.0 --thread-sim` 的 802.15.4 数据面：

- 构建 ESP-IDF `HA_on_off_switch` coordinator；
- 构建 ESP-IDF `HA_on_off_light` end device；
- 两个实例使用不同 UDP 端口启动；
- 本地 relay 只转发两端原始帧并记录方向、字节数和 hash；
- 从两端 UART 日志断言组网、steering、join 和 On/Off 生命周期。

## 构建

工程来自本地 ESP-IDF `v5.5.4`：

- `.work/esp-idf-v5.5.4/examples/zigbee/light_sample/HA_on_off_switch`
- `.work/esp-idf-v5.5.4/examples/zigbee/light_sample/HA_on_off_light`

两者均执行：

```bash
idf.py set-target esp32c6
idf.py build
```

结果 hash：

- switch image：
  `9d09ad38e19985c387957caab32111fef7568e387d13e7836b0614e72be8dfcd`
- switch ELF：
  `9fc1000e80f8d482e42942db96fa0da4a0eeb1aa2fec8bc115e0f30428347f24`
- light image：
  `de70918cdf45a4457ef6dc60e46c8903c44ccc1c0379ffb7aca29d9f9a5a1eef`
- light ELF：
  `6e54da13f1aaeb018b81491579a2c499efac4ca31e4a0951c0fdadc1cf4319ca`
- esp-emu：
  `a4c3468a4abf3f2e55ca0912fa7cdfbe5e101ecb6ab74a9ec35182d70ba6a771`

## 执行

使用仓库新增的可复现 runner：

```bash
python3 tests/firmware/c6_zigbee_thread_sim/run_feasibility.py \
  --emulator /path/to/esp-emu \
  --switch-image /path/to/switch/merged.bin \
  --switch-elf /path/to/switch/light_switch.elf \
  --light-image /path/to/light/merged.bin \
  --light-elf /path/to/light/light_bulb.elf \
  --timeout 35 \
  --out-dir /tmp/m5-c6-zigbee-thread-sim
```

runner 不使用 host-side Zigbee 状态或 fake radio payload；它只代理两个
guest 驱动产生的 802.15.4 原始帧。

## 结果

`status=PARTIAL`，`classification`：

```text
zigbee_commissioning_or_mac_ack_not_completed
```

观测：

- switch UART：`Formed network successfully`、network open、steering started；
- light UART：`Start network steering`；
- relay：switch→light 21 帧/685 bytes，light→switch 17 帧/198 bytes；
- 未出现 `Joined network successfully`；
- 未出现 `Received message: endpoint(10)` 或 `Light sets to ...`。

这说明 TCP/UDP bridge、双方 app boot 和至少部分 802.15.4 TX/RX 是工作的，
但 coordinator/end-device commissioning 尚未完成。最可能剩余边界是 MAC
ACK/关联时序或 `thread-sim` 未覆盖 Zigbee 所需的 controller 语义。

## 公开固件边界

公开 M5Burner NanoC6 Zigbee HA light 的 app image 为 `PARTIAL`，其
descriptor 记录 ELF SHA `e7126f...`。本地没有匹配 ELF，因此
`--thread-sim` 不能启用并安全验证该二进制。不能用不匹配 ELF 的运行结果
声明公开固件兼容，也不能用 host fake 值替代。

## 下一步

1. 在 backend 中补齐可验证的 802.15.4 MAC ACK/commissioning 语义；
2. 或取得公开固件的匹配 ELF/可重建源码并重跑同一 runner；
3. runner 必须观察到 join、On/Off 和离网后，才可从 `PARTIAL` 升级为 PASS；
4. WiFi/BLE/Zigbee coexistence 单独建门禁。

## 回滚

回滚 `321a2aa0c364c7c8e0fad2f926c236895faa8e52` 会移除 feasibility runner
和登记更新；旧的 QEMU watchdog evidence 不会受影响。

# 闭合复现与验证证据（2026-09-18）

## 环境

- macOS（Apple Silicon），Apple clang 21.0.0
- 可用：g++/clang++ 21、make、python3、git、gh
- 不可用：ESP-IDF（idf.py）、arduino-cli、esphome、platformio、cmake
- Arduino 工具链构建在本环境不可用，未执行

## 1. m5stack/M5Unit-8Encoder#7 — 运行时复现 PASS

- 固定版本：`a75ab1a0975f034cca4588b2c539d9dbb669cc2d`
- 方法：用 mock `Arduino.h`/`Wire.h` 编译真实 `UNIT_8ENCODER.cpp`，记录 `Wire.begin()` 收到的频率
- 未修复：`begin(..., 100000UL)` → `wire_begin_frequency=160`
- 仅把 `uint8_t _speed` 改为 `uint32_t _speed`：`wire_begin_frequency=100000`
- `requestFrom()` 返回 0 时，`getEncoderValue(0)` 仍读取 4 字节并返回 `-1`（`requested_len=4`）
- 源码 SHA256：`UNIT_8ENCODER.h f96dbbb8a53ec4cd4f5c9b83fc25eed18a7c27f3ac99b3f84bc2dae36682a44b`、`UNIT_8ENCODER.cpp 034f6da8adda9a8215a0bfe5bf18ef4235c521730073c9e9531bfae3f68950ed`
- 限制：host C++ harness，未使用 Arduino-ESP32 core，未上硬件

## 2. m5stack/StackChan-BSP#7 — 竞态复现 PASS（host/TSan）

- 固定版本：`8d4d6fc3b7a6be379c6317c45a02a30bff8c492e`
- 方法：真实 `motion.cpp` + `servo.cpp` + vendored uitk，stub FreeRTOS/Arduino，clang ThreadSanitizer
- 上游：6 个 data race；reader 栈为 `Motion::isYawMoving()/isPitchMoving()` → `Servo::isMoving()`，writer 栈为 `Motion::move()` → `Servo::moveWithSpeed()` → `AnimateValue::teleport()` → `Spring::init()`
- 在两个 getter 中加 `std::lock_guard` 后：0 个 TSan race warning，进程正常退出
- 相关代码：`src/M5StackChan.cpp:114`（`static SCSCL _scs_bus`）、`:203-208`（`_scs_bus.ReadMove()`）
- 源码 SHA256：`motion.cpp b79a642585fb457ee7d8330527179ea29d7903c84c6717ea626b51634b7e7e30`、`servo.cpp 8db05dabd2b18e58fabe956982f5c78a00a14c8fd9e65aa8beda0599a1e9fc3a`
- 限制：host harness，stub RTOS，未上硬件

## 3. m5stack/esphome-yaml#102 — 编译告警复现 PASS

- 固定版本：`cc708ddcc9dea7cfc746b408d2495ce281bbf2d2`
- 方法：用最小 ESPHome 头文件桩编译真实 `components/lp5562/lp5562.cpp`
- 未修复：`lp5562.cpp:61:9: warning: variable 'config_val' is uninitialized when used here [-Wuninitialized]`
- 改为 `uint8_t config_val = 0;` 后：同类未初始化告警为 0
- 限制：非完整 ESPHome/ESP-IDF 工具链

## 4. m5stack/StackChan#108 — 依赖 fetch 步骤 PASS，整机构建 NOT RUN

- 固定版本：`1b5765599fba8aaad1811d9a79358ccc7051f5f3`
- 执行 `python3 ./fetch_repos.py`，结果：
  - mooncake v2.3.3 `572a7e4`
  - mooncake_log v1.5.0 `554d55c`
  - smooth_ui_toolkit v2.12.0 `2a18ff5`
  - xiaozhi-esp32 v2.2.4 `e77dedb` + patch applied
  - ArduinoJson v7.4.2 `733bc4e`
  - esp-now `c33383d`
- `xiaozhi-esp32/main`、`components/ArduinoJson`、`components/esp-now` 均存在
- `idf.py build`：NOT RUN（本机无 ESP-IDF；未使用 Docker/其他绕过方式）

## 5. m5stack/StackChan#110 — 语义确认 PASS，行为复现 NOT RUN

- ESP-IDF v5.5.4 `esp_wifi_types_generic.h`：`WIFI_FAST_SCAN = 0`（注释：scan will end after find SSID match AP）
- 仓库 `wifi_station.cc:28-32` 对 `wifi_config_t` 做 `bzero` 后未设置 `scan_method` → 保持 0
- mesh/DHCP 现象：NOT RUN（需要设备与多 AP 环境）

## 公开发布

第一轮回复（2026-09-18 10:44 CST）：

- M5Unit-8Encoder#7 comment 5724382806
- StackChan-BSP#7 comment 5724383036
- StackChan#108 comment 5724381971
- StackChan#110 comment 5724383223
- esphome-yaml#102 comment 5724383408

验证补发（2026-09-18 10:58 CST）：

- M5Unit-8Encoder#7 comment 5724481495
- StackChan-BSP#7 comment 5724481711
- esphome-yaml#102 comment 5724481897
- StackChan#108 comment 5724482069
- StackChan#110 comment 5724482266

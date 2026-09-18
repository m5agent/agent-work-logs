# M5Stack GitHub 公开仓库：最近“没人回复”Issue 盘点与可回复性评估

- 生成时间：2026-09-18 10:45 CST
- 范围：GitHub 组织 `m5stack` 的公开仓库（不含 private 仓库）
- 口径修正：本报告“没人回复”= **`comments == 0`，即该 issue 下一条评论都没有**。
  - 上一版报告的“509 条无官方回复”是把“只有社区/提问者评论”也算进去，口径更宽。
  - **M5Unified#354 已由 m5agent 于 2026-09-17 回复过，不在本报告列表中**（该 issue 有 4 条评论）。
- 数据来源：GitHub Search API（`org:m5stack is:issue is:open`，618 条）+ 逐仓库源码核对（shallow clone，HEAD SHA 见下）。

## 一、最近完全无人回复的 Issue

### 近 30 天创建（10 条）

| 日期 | Issue | 标题 | 链接 |
| --- | --- | --- | --- |
| 09-17 | StackChan#119 | Weak and highly position-sensitive Wi-Fi signal on StackChan | https://github.com/m5stack/StackChan/issues/119 |
| 09-11 | uiflow-micropython#109 | ChainBus on second UART port fails with ESP_FAIL（≥2.4.x 回归） | https://github.com/m5stack/uiflow-micropython/issues/109 |
| 09-10 | esphome-yaml#109 | AtomS3R + Echo Base: continuous speaker noise from boot until first audio playback | https://github.com/m5stack/esphome-yaml/issues/109 |
| 09-06 | M5Unit-8Encoder#7 | begin() speed argument silently truncated by uint8_t _speed | https://github.com/m5stack/M5Unit-8Encoder/issues/7 |
| 09-02 | M5GFX#276 | CoreS3-SE FT6336U identity 64/03/20 triggers misleading version-read warning | https://github.com/m5stack/M5GFX/issues/276 |
| 08-30 | StackChan#117 | WPA2-Enterprise cannot be joined: ESP_WIFI_ENTERPRISE_SUPPORT disabled | https://github.com/m5stack/StackChan/issues/117 |
| 08-30 | StackChan#116 | Device reboots when companion app disconnects during WiFi setup | https://github.com/m5stack/StackChan/issues/116 |
| 08-25 | StackChan-BSP#7 | Motion::isYawMoving()/isPitchMoving() skip the mutex | https://github.com/m5stack/StackChan-BSP/issues/7 |
| 08-24 | M5_Hardware#19 | 结构文件丢失（StackChan 连接处） | https://github.com/m5stack/M5_Hardware/issues/19 |
| 08-20 | M5Unit-NFC#8 | ESP32C5 Support (Stamp-C5) | https://github.com/m5stack/M5Unit-NFC/issues/8 |

### 30–60 天创建（9 条）

| 日期 | Issue | 标题 | 链接 |
| --- | --- | --- | --- |
| 08-18 | StackChan#110 | WiFi provisioning never obtains IP on mesh networks（FAST_SCAN） | https://github.com/m5stack/StackChan/issues/110 |
| 08-07 | esphome-yaml#105 | Add support for the module Unit NFC | https://github.com/m5stack/esphome-yaml/issues/105 |
| 08-02 | StackChan#108 | Firmware does not build from a clean clone (IDF 5.5.5) | https://github.com/m5stack/StackChan/issues/108 |
| 07-30 | StackChan#105 | 手机 app 连接不上 StackChan | https://github.com/m5stack/StackChan/issues/105 |
| 07-29 | M5Dial#23 | determine power source (Ext/USB/Battery) | https://github.com/m5stack/M5Dial/issues/23 |
| 07-27 | AIFlow#3 | Windows 10 上启动几秒后退出 | https://github.com/m5stack/AIFlow/issues/3 |
| 07-26 | StackChan#104 | ESP-NOW Receiver mode instantly reboots | https://github.com/m5stack/StackChan/issues/104 |
| 07-24 | esphome-yaml#103 | AXP2101 Needs VBUS status sensors | https://github.com/m5stack/esphome-yaml/issues/103 |
| 07-20 | HAT_8Servos_v1.1_Firmware#1 | 多个固件问题（clamp 算术、steer_disable 极性、注释乱码） | https://github.com/m5stack/HAT_8Servos_v1.1_Firmware/issues/1 |

### 60–90 天创建（4 条）

| 日期 | Issue | 标题 | 链接 |
| --- | --- | --- | --- |
| 07-17 | StackChan#103 | TTS audio silent after camera.take_photo | https://github.com/m5stack/StackChan/issues/103 |
| 07-17 | M5StickC-Plus#66 | M5StickCPlus FactoryTest does not compile | https://github.com/m5stack/M5StickC-Plus/issues/66 |
| 07-16 | esphome-yaml#102 | Warning: config_val may be used uninitialized in lp5562.cpp | https://github.com/m5stack/esphome-yaml/issues/102 |
| 07-06 | esphome-yaml#99 | tab5-ha-hmi.yaml won't compile with ESPHome 2026.4.0+ | https://github.com/m5stack/esphome-yaml/issues/99 |

## 二、我已完成代码/配置核对的 Issue

以下核对均为当前公开仓库 HEAD 的只读源码检查；**未做整机/硬件复现**，涉及硬件现象的结论只作为待验证判断。

### A. 源码已确认，可直接给出实质回复

| Issue | 核对结论 | 关键证据（file:line @ commit） |
| --- | --- | --- |
| [M5Unit-8Encoder#7](https://github.com/m5stack/M5Unit-8Encoder/issues/7) | **Bug 确认**：`_speed` 是 `uint8_t`，`begin()` 收 `uint32_t` 后被截断，再传给 `Wire.begin()`；`readBytes()` 也没有检查 `requestFrom()` 返回值 | `src/UNIT_8ENCODER.h:23`（`uint8_t _speed;`）、`h:28-29`（`uint32_t speed`）、`src/UNIT_8ENCODER.cpp:25-32`（`_speed = speed; _wire->begin(...,_speed)`）、`cpp:19`（未检查 `requestFrom`）@ `a75ab1a0975f034cca4588b2c539d9dbb669cc2d` |
| [StackChan-BSP#7](https://github.com/m5stack/StackChan-BSP/issues/7) | **确认**：`Motion::isMoving()` 有 `_mutex`，`isYawMoving()` / `isPitchMoving()` 没有；且 `Servo::isMoving()` 会访问动画/协议状态，不只是读缓存 | `src/utils/motion/motion.cpp:128-142` @ `8d4d6fc3b7a6be379c6317c45a02a30bff8c492e` |
| [StackChan#116](https://github.com/m5stack/StackChan/issues/116) | **根因链确认**：`is_started_` 是实例成员，但 `esp_netif_create_default_wifi_sta()` 资源是进程级；断开后重建 `WifiConfigServer` → 新建 `StackChanWifiStation` → `Start()` 再跑一遍 → 默认 netif key 冲突断言 | `firmware/main/hal/utils/wifi_connect/wifi_station.cc:85-109`；`firmware/main/hal/hal_ble.cpp:348,512-514,537`；`firmware/main/apps/app_setup/workers/connectivity.cpp:142-150,212-213` @ `1b5765599fba8aaad1811d9a79358ccc7051f5f3` |
| [StackChan#117](https://github.com/m5stack/StackChan/issues/117) | **确认**：企业级 Wi-Fi 默认关闭；提问者已附“打开后可连接 PEAP/MSCHAPv2”的实测日志。是否支持属于产品决策，但事实层面可回复 | `firmware/sdkconfig.defaults:44`（`CONFIG_ESP_WIFI_ENTERPRISE_SUPPORT=n`）@ `1b576559...` |
| [StackChan#110](https://github.com/m5stack/StackChan/issues/110) | **确认**：`wifi_config_t` 先 `bzero`，随后只填 `ssid`/`password`，`scan_method` 保持 0（`WIFI_FAST_SCAN`），多 AP 同 SSID 时可能连到弱 BSSID | `firmware/main/hal/utils/wifi_connect/wifi_station.cc:28-34` @ `1b576559...` |
| [StackChan#108](https://github.com/m5stack/StackChan/issues/108) | **不是代码 bug，是缺少构建前置步骤**：仓库要求先运行 `python3 ./fetch_repos.py` 拉取 `xiaozhi-esp32`、`ArduinoJson`、`esp-now`、`mooncake` 等依赖并打 patch，然后才能 `idf.py build` | `firmware/README.md`（Build → Fetch Dependencies）；`firmware/repos.json:18-31`；`firmware/main/CMakeLists.txt:2,314-315` @ `1b576559...` |
| [M5GFX#276](https://github.com/m5stack/M5GFX/issues/276) | **确认逻辑**：`initPanelByTouchVersion()` 只在 `VENDID==0x11` 且 `FIRMID∈{0x10,0x12}` 时认为有效，否则告警并按 ILI9342C 处理；是否把 0x64/0x03/0x20 纳入属维护者判断（硬件侧未复测） | `src/M5GFX.cpp:605-660`（校验在 624-640）@ `641944bd5b123e42b6f4379ff16768e292e203d1` |
| [HAT_8Servos_v1.1_Firmware#1](https://github.com/m5stack/HAT_8Servos_v1.1_Firmware/issues/1) | **clamp 算术 bug 确认**：应为 `list_ptr->len - offset`，实际写成 `list_ptr->len - len`，越界时结果错误甚至为负 | `Myfile/i2c_ex.c:183`；另 `Myfile/Steer.c:131-141` 为 `steer_disable` 极性相关代码 @ `4c5dc449493276c44e6881947abdff47813f0ae5` |
| [esphome-yaml#102](https://github.com/m5stack/esphome-yaml/issues/102) | **确认**：`uint8_t config_val;` 未初始化就做 `|=`，编译器告警成立，改成 `= 0` 即可 | `components/lp5562/lp5562.cpp:58-72` @ `cc708ddcc9dea7cfc746b408d2495ce281bbf2d2` |

### B. 配置/API 层可回复，但结论需说明未做整机验证

| Issue | 核对结论 | 说明 |
| --- | --- | --- |
| [esphome-yaml#109](https://github.com/m5stack/esphome-yaml/issues/109) | NS4150B 功放开关配置为 `restore_mode: RESTORE_DEFAULT_ON`，确实会在 ES8311/I2S 建立前就使能功放；提问者的怀疑与配置一致 | 证据：`common/atoms3r-with-echo-base.yaml:258-267`，ES8311 在 `171-177` @ `cc708dd...`。噪声是否消失需 AtomS3R+Echo Base 实物复测 |
| [M5Dial#23](https://github.com/m5stack/M5Dial/issues/23) | M5Unified 提供 `M5.Power.getVBUSVoltage()` 和 `M5.Power.isCharging()`，可用于判断 USB/VBUS 是否供电；M5Dial 的 PMIC 型号建议由维护者确认后再给最终答复 | 证据：`src/utility/Power_Class.hpp:182,184-187` @ `e79eb6e3137a41e50b0ec23c8c38738bdb3a11e2` |

## 三、需要硬件/环境才能验证，暂不宜代答

| Issue | 原因 |
| --- | --- |
| StackChan#119 | Wi-Fi RSSI/位置敏感性需要设备 + AP 实测，且提问者明确要求 M5Stack 提供 raw RSSI 对比 |
| uiflow-micropython#109 | 需要 DualKey 实物 + 2.3.9/2.5.3 两版固件复现；可先做 tag 间源码 diff 定位 |
| StackChan#105 / #104 / #103 | 分别涉及 iOS App 配对、ESP-NOW 重启、TTS/摄像头时序，均需整机复现 |
| AIFlow#3 | Windows 10 环境问题，本机为 macOS，无法复现 |
| M5_Hardware#19 | 3D 结构件缺失需要 CAD/结构工程师确认；仓库 `Products/K151_StackChan/Structures` 下确无明显的连接环文件 |
| M5Unit-NFC#8 / esphome-yaml#105 / esphome-yaml#103 | 属功能请求/路线图决策，需要产品与维护者定方向 |
| M5StickC-Plus#66 / esphome-yaml#99 | 需要对应构建环境（Arduino / ESPHome 2026.4.0+）实测编译 |

## 四、建议优先回复的 Issue

1. **StackChan#108** — 直接给出构建步骤（`python3 ./fetch_repos.py`），问题可闭环。
2. **M5Unit-8Encoder#7** — 确认 bug + 建议把 `_speed` 改为 `uint32_t`、并检查 `requestFrom()` 返回值。
3. **StackChan-BSP#7** — 确认缺少锁，建议为两个 getter 加 `std::lock_guard`（或统一走 `isMoving()` 封装）。
4. **StackChan#110** — 确认 `scan_method` 默认 FAST_SCAN，建议设 `WIFI_ALL_CHANNEL_SCAN` + 按信号排序。
5. **StackChan#117** — 可以先说明默认关闭的现状与提问者的可用方案，同时请维护者决定是否接受 PR。
6. **esphome-yaml#102** — 一行修复确认，适合快速闭环。
7. **M5GFX#276** — 说明告警触发条件，请维护者确认是否扩大 FT6336U 身份白名单。

## 五、限制与发布流程

- 本报告**没有向任何 issue 发表评论**，只做了公开数据读取与本地只读源码核对。
- 代码核对基于当前 HEAD（快照 commit 见上），不是对报告者所用版本（如 M5GFX 0.2.27、固件 2.5.3）的逐版本复核。
- 未执行：整机硬件复现、ESP-IDF/Arduino/ESPHome 实际构建、private 仓库检查。


## 闭合复现与验证（2026-09-18 更新）

在首轮公开回复后，对 5 条 issue 做了可执行验证，详见 `evidence/verification.md`：

| Issue | 验证级别 | 结果 |
| --- | --- | --- |
| M5Unit-8Encoder#7 | host 运行时复现（真实库源码 + mock Wire） | PASS：上游 160 Hz；改为 `uint32_t` 后 100000 Hz；`requestFrom()` 失败时返回 -1 |
| StackChan-BSP#7 | host ThreadSanitizer（真实 motion.cpp/servo.cpp） | PASS：上游 6 个 data race；两个 getter 加锁后 0 个 |
| esphome-yaml#102 | 真实源文件编译告警复现 | PASS：`config_val` 未初始化告警；加 `= 0` 后消失 |
| StackChan#108 | 实际执行依赖 fetch 脚本 | PASS（fetch 层）：6 个依赖按声明版本就位、patch 已应用；`idf.py build` NOT RUN |
| StackChan#110 | ESP-IDF v5.5.4 头文件确认 | PASS（配置语义）：`WIFI_FAST_SCAN = 0`；mesh 行为 NOT RUN |

仍未执行：ESP-IDF/Arduino/ESPHome 完整工具链构建与实机复现。Arduino 工具链构建在本环境不可用，未执行。

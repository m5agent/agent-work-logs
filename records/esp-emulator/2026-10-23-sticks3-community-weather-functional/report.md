# StickS3 校园天气机 v1.0.0 虚拟设备功能验证报告

## 背景

目标是在 StickS3 虚拟设备上选择一个带网络的社区用户固件，验证实时数据、页面显示、按键和声明的完整功能。

选中 M5Burner 社区项目 **StickS3 校园天气机 v1.0.0**：

- 固件 ID：`2108939572843147265`
- 版本 ID：`2109509580358971393`
- 源码：<https://github.com/LamZaakDok/sticks3-weather-clock>
- M5Burner：<https://burner.m5stack.com/firmware/2108939572843147265>

固件声明横屏时钟、农历/干支、7 个天气页、Open-Meteo 数据、动态图标、预警、离线语音、闹钟、息屏、AP 配网、WiFi OTA，以及 KEY1/KEY2 操作。

## 源码与镜像

`v1.0.0` 标签为 `cb437d240fc906b5540aec530dc4863019116ce9`。当前源码 HEAD `d9334919df95cb5250de9e0e36d027b801325304` 只新增整包合成脚本；`src/`、`data/` 和 `platformio.ini` 无差异。

| 项目 | 结果 |
| --- | --- |
| 发布文件 | `sticks3-weather-full.bin`，`8323072` bytes |
| 发布 SHA256 | `8b7b47c8d601e1821817f8d0e6b55568829913e50333dbcc15de6ffdbad1997c` |
| 合成 Flash | `8388608` bytes |
| 合成 SHA256 | `d291e77f782399e37fd5b464f9b206a00654b2c10556d730d1c45667156c603f` |
| 芯片 | ESP32-S3 |
| app0 | `0x10000`，`3342336` bytes |
| LittleFS | `0x670000`，`1572864` bytes，207 个条目 |
| LittleFS SHA256 | `c7b4574299ae97072449ff7d9be24aca816dd4ec6aff54446ae3dc438af5e45c` |

镜像头部、分区表、应用和音频文件系统均有效，未发现发布镜像缺应用或缺语音素材的问题。

## 发布镜像在 QEMU 中的结果

镜像可启动，M5GFX 识别为 `board_M5StickS3`，随后显示“手机配网 / StickS3-Weather / 设备配网地址”。串口同时出现：

```text
Preferences: nvs_get_str ... NOT_FOUND
esp_littlefs: Corrupted dir pair at {0x0, 0x1}
esp_littlefs: mount failed, (-84)
WiFiSTA: connect failed
```

这不是天气数据造假：应用还没有进入 Open-Meteo 请求，原因是当前 QEMU 中 NVS 保存的 WiFi/城市和 LittleFS 语音分区没有正确读出。

## NVS 兼容性控制

使用相同 Arduino-ESP32 2.0.17 环境做独立控制：

1. 不启用 PSRAM：

   ```text
   write=6 readback=myssid
   ```

   `PASS`。

2. 启用 StickS3 的 `qio_opi` / PSRAM：

   ```text
   psramInit(): PSRAM enabled
   write=6 readback=
   ```

   NVS 写入返回成功，但立即回读为空。

3. 在天气机源码中把配置写入 NVS 后再回读，仍得到空值；LittleFS 也会在格式化后立即读取失败。

因此当前能确认的是：问题位于 **ESP32-S3 QEMU + Arduino-ESP32 2.0.17 + PSRAM/M5 初始化路径的 Flash/NVS/LittleFS 数据面兼容性**。根因尚未修复，所以没有把原始发布镜像的完整功能标为 PASS。

证据：

- `evidence/network/arduino-nvs-control-no-psram-serial.log`
- `evidence/network/arduino-nvs-control-psram-serial.log`
- `evidence/network/marker-summary.txt`

## 网络结果

### esp-emu

源码固定到发布版本并加入确定性测试 provisioning 后，esp-emu 串口显示 NVS 在 M5 初始化前后均可回读，随后应用进入 ArduinoOTA：

```text
stage=after-preseed ssid='<test SSID>'
stage=after-m5begin ssid='<test SSID>'
ArduinoOTA: OTA server at: sticks3-weather.local:3232
```

应用只有 `wifiConnect()` 成功后才调用 `setupOta()`，所以这组证据闭环了 NVS 持久化、WiFi 关联和 OTA 初始化。

对应证据：`evidence/network/esp-emu-wifi-nvs-ota.json`、`evidence/network/esp-emu-wifi-serial.log`。

### Open-Meteo

设备随后尝试 geocoding、forecast 和 air-quality HTTPS，但没有出现 `[geo]`、`[wx] ok` 或 `[air] aqi`。受限运行时 TLS 被重置；非受限运行时停在 geocoding 连接阶段。

主机侧在同一时间访问：

- 深圳 geocoding：HTTP 200，纬度 `22.54554`、经度 `114.0683`；
- forecast：HTTP 200，温度 `31.3°C`、湿度 `40%`、weather code `0`。

这些只是主机控制数据，没有写入或伪装成设备结果。设备页面中的 `--` 与“时间同步中”对应数据未闭环。

证据：`evidence/network/host-open-meteo-control.json`、`evidence/network/esp-emu-public-data-attempt.json`。

## 显示与按键

为绕过配网阻塞，使用同一页面绘制代码构建 UI/输入 harness。该 harness 不向天气对象注入伪造数据。

### KEY1

连续 8 次单击得到 8 个不同帧：

| 次数 | 页面 | SHA256 |
| --- | --- | --- |
| 1 | 今日 | `4aaf80e2a011b70efdf407109a68a6e746fda520ca815c3271f3e7925602c7ee` |
| 2 | 未来 5 天 | `2f637a045304fd8c9dc4b8fe685d8f47e4a9c10c3ff74acc83b7bedb34fcdaf0` |
| 3 | 防晒指数 | `fa27127d0d2c0da885bfe8e2ec72e1509ee1c0f2dff834c6a94dd20e00ab8eac` |
| 4 | 生活提示 | `777054f846de0c09fa83e1dfcf01d41c450d472562952f7bd841c4326acf0401` |
| 5 | 未来 24 小时 | `3271310bab47faaa8dd4f23346163e37a0e2a7d14638029e808da239feac520b` |
| 6 | 空气质量 | `51f8f620eafa3bc28f981b13a82bb7497ff57ee70e599e5c8bddf8cdd1c29ae1` |
| 7 | 洗晒指数 | `4322daa034b102628f65c76430acf5c5be4bc6b9cfc87ee4f431945ad4067b41` |
| 8 | 时钟 | `5c89a0b16b9a7284e678fce639a1a2bb9766c0be61836237f832689413e22422` |

第 8 帧回到初始时钟，符合 `(g_seq + 1) % 8`。

### KEY2

- 单击：先出现“网络已断开”，随后回时钟，响应帧哈希 `666189f7b353bf07d0d2323a9d700ad6fdf34f27bf2cca2ebdab06dfa99cb889`。`PASS`。
- 双击：没有观察到设置热点入口。`NOT RUN`。
- 长按 3 秒：没有观察到重启或重新配网入口。`NOT RUN`。
- KEY1 长按播报：LittleFS 未挂载，语音无法播放。`NOT RUN`。

### 显示边界

页面标题和部分内容可读，但所有页面截图都出现上下半屏重复/切块，例如生活提示卡片在下半屏再次出现，洗晒页的 `100` 再次被放大复制。

因此不能把截图直接判成用户 UI 代码错误；但没有实体 StickS3 对照，真实布局质量只能记为 `PARTIAL`。

## 验证矩阵

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 发布镜像静态校验；同源 harness 编译成功 |
| flash | `PASS` | 完整镜像校验并启动 QEMU |
| transport | `PARTIAL` | esp-emu NVS、WiFi 关联、OTA 初始化通过；设备侧 HTTPS 未闭环 |
| device_response | `PARTIAL` | KEY1 8 页、KEY2 单击通过；双击/长按/语音未覆盖 |
| data_behavior | `FAIL` | 设备未获得天气 JSON，未显示实时温度/湿度/AQI |
| visual_or_physical | `PARTIAL` | 页面标签和帧转换正确，但 QEMU 输出有重复切块 |
| physical_hardware | `NOT RUN` | 实体 StickS3 测试槽离线 |

## 边界与后续条件

- 本结果是 **virtual-device validation**，不是物理硬件、RF、功耗或电气测量。
- 需要在 ESP32-S3 QEMU 中修复 NVS/LittleFS/PSRAM 数据面，才能验证原发布镜像的配网页、语音和真实天气。
- 需要设备侧公网 HTTPS 成功并记录响应，才能把数据层从 `FAIL` 提升。
- 需要实体 StickS3 验证真实屏幕、音频、电池与无线行为。

## 风险与回滚

所有操作都在一次性虚拟 Flash 会话中完成，没有写入实体设备，没有修改发布固件或用户源码，原始发布 SHA256 保持不变；无不可逆硬件操作需要回滚。

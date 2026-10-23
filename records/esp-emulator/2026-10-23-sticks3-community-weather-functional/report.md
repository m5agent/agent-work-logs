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
ArduinoOTA: OTA server started (mDNS suffix redacted)
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

## 后续复测：S3 QIO 读阶段修复

### 修正后的根因

初始记录把问题归在 PSRAM/M5 初始化后的 Flash/NVS/LittleFS 组合路径，
方向正确，但仍过于上层。后续用发布源码同版本的 Arduino 探针直接调用：

```text
esp_flash_erase_region(0x7F0000, 4096)
esp_flash_write(pattern, 0x7F0000, 4096)
esp_flash_read(readback, 0x7F0000, 4096)
```

修复前写入和擦除均返回 `ESP_OK`，PSRAM pattern 错误为 0，但 4096 个
Flash 回读字节全错；关闭会话后，虚拟 Flash 后端确实保存了写入内容。因此
问题不是 NVS、LittleFS、PSRAM 或后端持久化，而是 S3 的低层 Flash 读路径。

QEMU trace 显示 `0xEB` QIO 命令进入 `m25p80` 时，控制器只发送了：

```text
0xEB + 3-byte address + 1 dummy byte
```

`m25p80` 的 QIO 状态机则需要：

```text
0xEB + 3-byte address + mode + 4 dummy bytes
```

因此每轮读都少了四个字节，前四个真实数据字节被当作头部吞掉，后续数据整体
左移。NVS 空值、LittleFS 损坏和画面下半部重复都是同一个读偏移造成的。

最小修复位于 QEMU `hw/ssi/esp32s3_spi.c`：只对 flash CS0 上的 `0xEB`
QIO read 补足 `m25p80` 所需的五字节 post-address phase。patch 针对
`espressif/qemu da100c909249926b9f4458f18e4f2d216d08f51a`，
反向校验通过。

### 修复后执行

1. 重建 `qemu-system-xtensa`。
2. 通过 Device Service 启动 raw Flash 探针：
   `afbfc12762214d8aa30716e454ff74b5`。
   - erase/write/read 均为 `0x0`；
   - 4096-byte pattern 错误数为 0；
   - NVS `write=6 readback=myssid`。
3. 通过 Device Service 启动原始发布镜像 app0 与原始 LittleFS：
   - app0 SHA256 `cd1b0d9868a9ff3f6fd7fb027075d5f0405a488a8bcd007dc806a599c6fb0811`；
   - LittleFS SHA256 `c7b4574299ae97072449ff7d9be24aca816dd4ec6aff54446ae3dc438af5e45c`；
   - 仅替换隔离 runtime NVS，SHA256 `22506441e305f857d5abd780bc743185678229b28d63f6d20b9680c9eaae9d48`；
   - 发布文件 SHA256 保持
     `8b7b47c8d601e1821817f8d0e6b55568829913e50333dbcc15de6ffdbad1997c`。
4. weather session `c896d0840275404b92e6814a5788bc36`：
   - M5GFX 识别 `board_M5StickS3`；
   - ArduinoOTA 初始化证明 `WiFiConnect()` 已返回；
   - 今日页显示深圳、31 C、体感 31 C、湿度 40-41%、风速 14.2 m/s；
   - 空气质量页显示 AQI 104-105、PM2.5 39-40、PM10 39-40。
5. 八页逐页截图后组成总览，所有页面完整，原有上下半屏重复消失。

天气值来自设备侧 Open-Meteo 请求路径，没有向天气对象注入宿主值。网络模型
曾经在一次会话中停在 geocoding 等待，因此网络稳定性仍应单独做重复压测；
本次已明确取得设备侧实时数据，不再把数据层记为 `FAIL`。

### KEY2 与配网页

- 单击刷新：出现“正在更新天气... 深圳”，随后回到天气页，`PASS`。
- 长按 3 秒：出现“重新配网 / 清除 WiFi 后重启”，`PASS`。
- 双击：仍为 `FAIL`，但原因已确认在第三方应用，不是 QEMU。
  [main.cpp L358-L368](https://github.com/LamZaakDok/sticks3-weather-clock/blob/cb437d240fc906b5540aec530dc4863019116ce9/src/main.cpp#L358-L368)
  在 350 ms 时清除 `bPending`，而 M5Unified 的
  `wasDoubleClicked()` 要等到其 500 ms click-count 决策窗口结束后才为真，
  因此设置热点分支实际上不可达。
- 长按后的首次 warm restart 在测试窗口内没有重新进入应用；把保留的虚拟
  Flash 冷启动后能进入 AP 配网页。该 warm-restart 复测记为 `PARTIAL`。
- 配网页 HTTP 未执行：AP 位于 guest-local netif，Device Service 当前没有到
  guest-local AP 地址的主机路由或 host-forward。

### 语音与回归

KEY1 长按触发语音，session `489826b092bf49ffb8ee4ac269cdbcbf`
输出 `68608` bytes PCM：

```text
2.144 s @ 16 kHz mono
unique_samples=1339
peak=1273
rms=178.06
```

文件系统未挂载或音频文件缺失时不会产生这段有内容的波形。因此原始
LittleFS 语音素材、解码和 I2S TX/GDMA 路径已经闭环。

仓库回归：

| 检查 | 状态 |
| --- | --- |
| `platform/tests` 单元测试 | `PASS`，171 tests |
| runtime coverage | `PASS` |
| peripheral catalog | `PASS` |
| StickS3 外设矩阵 | `PASS`，5/5 cases |

### 更新后的分层结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | QEMU 重建、patch reverse-check、平台检查 |
| flash | `PASS` | 原始镜像经 Device Service 写入隔离虚拟 Flash |
| transport | `PASS` | raw SPI Flash、NVS、WiFi association/DHCP/data path |
| device_response | `PARTIAL` | 八页、刷新、长按、语音通过；双击由应用逻辑失败 |
| data_behavior | `PASS` | 设备侧实时 Open-Meteo 天气和空气质量显示 |
| visual | `PASS` | 八页完整，无切块或重复 |
| portal | `PARTIAL` | AP 画面通过；网页 HTTP 与 warm-restart 未完整闭环 |
| physical_hardware | `NOT RUN` | 无实体 StickS3、RF、功耗和电气测量 |

## 风险与回滚

所有操作都在一次性虚拟 Flash 会话中完成，没有写入实体设备，没有修改发布固件或用户源码，原始发布 SHA256 保持不变；无不可逆硬件操作需要回滚。

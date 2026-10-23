# StickS3 校园天气机 v1.0.0 虚拟设备功能验证

- 日期：`2026-10-23`
- 结果：`PARTIAL`
- 工作类型：`hardware_test`（virtual-device validation）
- 固件：M5Burner `2108939572843147265` / `1.0.0`
- 源码：`LamZaakDok/sticks3-weather-clock @ cb437d240fc906b5540aec530dc4863019116ce9`
- 环境：StickS3 QEMU 与 esp-emu；PlatformIO Core 6.2.0；Arduino-ESP32 2.0.17；M5GFX 0.2.32

## 初始结论

发布镜像、`v1.0.0` 源码和声明的 7 个天气页 + 时钟页能够对齐。KEY1 连续 8 次得到 8 个不同帧，依次进入今日、未来 5 天、防晒指数、生活提示、24 小时趋势、空气质量、洗晒指数并回到时钟；KEY2 单击也产生了“网络已断开”的可见响应。

但本次不能判为完整 PASS：QEMU 中该 Arduino 4.4 固件的 NVS 和 LittleFS 数据面不稳定，发布镜像原样运行会停在配网页；esp-emu 证明了 NVS 持久化、WiFi 关联和 OTA 初始化，但设备侧 Open-Meteo HTTPS 没有返回天气数据。QEMU 截图还存在上下半屏重复/切块，语音、双击、长按和实体硬件仍未覆盖。

## 后续结论

同一问题的后续复测已完成。根因是 ESP32-S3 `0xEB` QIO 读阶段少了四个字节：
Arduino ESP32 4.4 只发送一个 dummy 字节，而 QEMU `m25p80` 将五个字节
视为模式/dummy 阶段，随后吞掉前四个真实数据字节。修复后：

- 4 KiB Flash 擦写回读 `errors=0`，NVS 写入/回读通过；
- 原始发布镜像的 app0 和 LittleFS 字节保持不变，配网状态来自隔离 runtime NVS；
- 设备侧实时天气页显示深圳、31 C、湿度 40-41%、风速 14.2 m/s、AQI 104-105；
- KEY1 的八个页面全部完整，无上下半屏切块；
- KEY1 长按输出 2.144 秒非静音 PCM，证明 LittleFS 语音素材和 I2S 播放路径；
- KEY2 单击刷新和长按重新配网都有可见响应，冷启动可进入 AP 配网页。

整体仍为 `PARTIAL`：KEY2 双击被第三方应用自身的 350 ms 超时逻辑提前取消，
早于 M5Unified 的 500 ms 双击决策；配网页 HTTP 因 guest-local AP 无主机路由
未执行；实体硬件、RF、功耗和电气测量仍未运行。

## 关键证据

- 发布镜像：`8323072` bytes，SHA256 `8b7b47c8d601e1821817f8d0e6b55568829913e50333dbcc15de6ffdbad1997c`
- 合成 Flash：`8388608` bytes，SHA256 `d291e77f782399e37fd5b464f9b206a00654b2c10556d730d1c45667156c603f`
- LittleFS：207 个条目，SHA256 `c7b4574299ae97072449ff7d9be24aca816dd4ec6aff54446ae3dc438af5e45c`
- KEY1：`8/8` 帧哈希不同，第 8 帧回到时钟
- esp-emu：NVS seed、M5 初始化后 NVS 回读、WiFi 关联、ArduinoOTA 初始化均通过
- 主机控制：深圳 geocoding 和 forecast 均 HTTP 200；设备侧未得到对应数据

## 文件

- `report.md`：完整分析、验证矩阵、根因边界
- `run.json`：机器可读记录
- `evidence/ui/`：页面截图、帧哈希、KEY2 响应和状态快照
- `evidence/network/`：发布镜像、esp-emu 和主机控制证据
- `evidence/followup-2026-10-23-qio-read-fix/`：QIO 根因、原始固件实时天气、八页完整布局、刷新/重配网和 PCM 证据
- `patches/0001-esp32s3-qio-read-phase.patch`：可应用到 QEMU base commit 的最小修复

## 未覆盖项

- 设备侧实时天气：`FAIL`
- 真实页面视觉质量：`PARTIAL`，虚拟帧有重复切块
- 语音、闹钟、双击、长按、配网页、OTA 升级：`NOT RUN`
- 实体硬件、RF、功耗和电气行为：`NOT RUN`

# 报告：StackChan #140 AI.AGENT 语音播放可选试验

## 1. 背景与目标

[#140](https://github.com/m5stack/StackChan/pull/140) 针对 #54 的 AI.AGENT 英文语音断字问题，
提出一个默认关闭的构建选项 `CONFIG_STACKCHAN_AI_AUDIO_TRIAL`：

- OTA 同时给出 MQTT 与 WebSocket 时优先 WebSocket；只有 MQTT 时保持原路径；
- WebSocket 路径的接收回调在 decode queue 满时等待空位；MQTT-only 会话保持非阻塞；
- CoreS3 的 I2S 双向 ring 从 6 个 DMA descriptor 改为 8 个
  （24 kHz、每 descriptor 240 frame，即 60 ms → 80 ms）。

作者声明：单台 CoreS3 StackChan、官方 1.6.2 镜像；未测 queue drop、I2S underrun、打断时延，
也没有第二台设备；100 ms 试验出现过启动阶段 HTTP 发送失败。

评审目标：确认补丁可应用、可构建、默认路径不变，并在本机可用的证据层级上验证运行时初始化，
同时给出未覆盖项。

## 2. 改动面

`git diff 28b9f0c..30820d66`：3 文件 +74/−8。

| 文件 | 内容 |
| --- | --- |
| `firmware/main/Kconfig.projbuild` | 新增 `STACKCHAN_AI_AUDIO_TRIAL`，`depends on BOARD_TYPE_M5STACK_STACK_CHAN`，`default n` |
| `firmware/patches/xiaozhi-esp32.patch` | `InitializeProtocol` 选择 WebSocket、把 flag 传给 `PushPacketToDecodeQueue`；`CreateDuplexChannels` 的 `dma_desc_num` 6→8 |
| `firmware/README.md` | 选项说明、比较方法、内存提示 |

patch 的其余大段内容（activation/App binding、CoreS3 codec 的 PCM32 写入等）是 1.6.2 已有内容，
不是本 PR 引入。

## 3. 代码核对

### 3.1 选项作用域与默认路径

- `firmware/main/Kconfig.projbuild:17-26`：选项位于 “Xiaozhi Assistant” menu，依赖
  `BOARD_TYPE_M5STACK_STACK_CHAN`（同一文件 `:261` 的板卡 choice），默认 `n`。
- 关闭时 `application.cc:546` 为 `constexpr bool prefer_websocket = false;`，协议选择仍是
  “有 MQTT 就用 MQTT”，回调仍是原来的非阻塞 `PushPacketToDecodeQueue(packet)`（第二参数默认
  `false`，`audio_service.h:144`）。
- 打开时 `application.cc:544` 用 `ota_->HasWebsocketConfig()`；`application.cc:548-553`
  先看 MQTT 再看 WebSocket，与原来一致的 fallback 结构。

### 3.2 等待语义

`audio_service.cc:609-627`：

```cpp
if (audio_decode_queue_.size() >= MAX_DECODE_PACKETS_IN_QUEUE) {
    if (wait) {
        audio_queue_cv_.wait(lock, [this, generation]() {
            return service_stopped_.load() || generation != playback_generation_ ||
                   audio_decode_queue_.size() < MAX_DECODE_PACKETS_IN_QUEUE;
        });
    } else {
        return false;
    }
}
```

`Stop()`（`:173-190`）和 `ResetDecoder()`（`:798-813`）都在持 `audio_queue_mutex_` 时
`++playback_generation_` 并 `notify_all()`；decode 侧 `:397-400` 弹出 packet 后也
`notify_all()`。因此等待会在“队列出现空位 / 服务停止 / generation 变化”三种情况下返回，
不会因停止或打断永久挂住。队列上限 `MAX_DECODE_PACKETS_IN_QUEUE = 1200/60 = 20` 包
（`audio_service.h:43`），即约 1.2 s 音频。

### 3.3 接收回调所在任务

`websocket_protocol.cc:108` 的 `websocket_->OnData(...)` 同时处理 binary 音频与 JSON 控制消息。
把 `wait=true` 放在这里，意味着 decode queue 满时该回调会阻塞到队列出现空位（正常播放时约为
一个 60 ms 包的时间），期间同一回调上的 JSON 控制消息（如 `tts stop`/abort）也会被推迟。
这是本试验需要测“打断时延”的原因；按上面的队列上限与唤醒条件，它不是永久阻塞，也不是死锁。

### 3.4 内存代价

IDF v6.1 `i2s_common.c:624-655` 的 DMA buffer 大小为
`dma_frame_num × bytes_per_sample × active_slot`；`i2s_std.c:150` 对 mono 取 1 个 active slot，
`i2s_tdm.c:160` 对 TDM 取 slot mask 的 popcount。

- TX（`esp_codec_dev` open 后 32-bit、channel=1）：1 slot × 4 B × 240 = 960 B/descriptor；
- RX（TDM 4 slots × 16-bit）：4 × 2 B × 240 = 1920 B/descriptor；
- 两个方向各多 2 个 descriptor：`2×960 + 2×1920 = 5760 B` 内部 DMA RAM。

这是运行时分配，静态 map 不变（见构建结果）。

## 4. 构建

- 依赖：`python3 fetch_repos.py`，xiaozhi-esp32 落在 `49b4380b`（v2.5.2），patch 应用成功。
- 工具链：ESP-IDF v6.1，`esp32s3`，16 MB flash，8 MB PSRAM。
- 默认配置：`idf.py -B build-off build` → exit 0，app 3777808 B，
  SHA-256 `7e761627…f682`。
- 试验配置：`sdkconfig.defaults.local` 写入 `CONFIG_STACKCHAN_AI_AUDIO_TRIAL=y` 后重建 →
  exit 0，app 3777808 B，SHA-256 `1bda0b3a…de68`；`sdkconfig.h` 有对应 define。
- 静态尺寸两者完全相同：Flash Code 2676904、Flash Data 932732、DIRAM 207868/341760。
- 机器码：`CreateDuplexChannels` 中 `dma_desc_num`（栈偏移 172）的立即数在关闭时为 6、
  打开时为 8。

## 5. 虚拟设备验证

环境：本机 Device Service 的 `stackchan` profile，qemu 运行时（ESP32-S3，16 MB flash，
8 MB PSRAM）。两次会话使用 merged 16 MB 镜像，SHA-256 分别为
`251eb220…df487`（试验）与 `22295b2e…34796`（原版）。

执行路径：会话进入 `running` → 画面 Welcome → touch Skip → launcher → touch AI.AGENT 图标。
AI.AGENT 打开时串口输出：

```text
I (33383) CoreS3AudioCodec: Audio IOs: mclk: 0, bclk: 34, ws: 33, dout: 13, din: 14
W (33383) i2s_common: the rx channel on I2S0 is switched from master to slave for full-duplex mode
I (33393) CoreS3AudioCodec: Duplex channels created
I (33403) ES7210: Enable ES7210_INPUT_MIC1/2/3
I (33413) ES7210: Enable TDM mode
I (33413) CoreS3AudioCodec: CoreS3AudioCodec initialized
I (33413) AudioCodec: Audio codec started
I (33423) SystemInfo: free sram: 70495 minimal sram: 40592
```

原版同路径为 `CoreS3AudioCodec initialized` 后
`I (23233) SystemInfo: free sram: 76407 minimal sram: 40356`。

差值 5912 B，与按 IDF 公式计算的 5760 B 一致（差值为堆管理/其它运行时分配噪声）。
这是单次采样，不是统计测量；但它验证了“8 个 descriptor 能初始化”以及“额外开销量级”。

打开 AI.AGENT 后设备提示 `WiFi setup required` 并重启进入 App 配网，因此没有进入 OTA、
MQTT 或 WebSocket 会话，也没有音频流。

## 6. 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | 两种配置 ESP-IDF v6.1 构建 exit 0；镜像哈希已记录 |
| flash / boot | PASS | 虚拟 StackChan 从 merged 镜像启动，8 MB PSRAM，应用 1.6.2 |
| device_response | PASS | AI.AGENT 打开后 codec/I2S/ES7210 初始化日志，无 I2S 错误 |
| data_behavior | NOT RUN | 无 WebSocket/MQTT 音频流、无 OTA 响应 |
| visual_or_physical | NOT RUN | 无扬声器/麦克风声学测量、无实机 |
| review | PASS | patch 应用、Kconfig 作用域、等待语义与内存计算已核对 |

## 7. 评审结论与风险

未发现阻塞问题。两个非阻塞点：

1. **内存**：+5760 B 内部 DMA RAM（虚拟设备单次采样 −5912 B free SRAM）。作者已提示
   内部内存余量；这个数字可以直接用于 80 ms/100 ms 两档的预算比较。
2. **试验的 WebSocket 优先没有 MQTT 回退**：OTA 同时给出两种配置时，试验版总是选 WebSocket；
   若网络只允许 MQTT，设备会走 WebSocket 错误路径。作为 opt-in 试验可接受，但测试者应把它
   与“变差”区分开。

另外，等待发生在 WebSocket 的单一 `OnData` 回调上，会同时推迟控制 JSON；由于队列上限
（20 包）与 stop/reset 唤醒条件，阻塞有界，但“打断时延”确实需要作者补测。

## 8. 验证边界与补测条件

- 语音断字是否改善、I2S underrun/drop、queue drop、首音时延、打断时延、唤醒词、重连：
  需要 StackChan OTA/MQTT/WebSocket 服务端与可听的输出，`NOT RUN`；
- 运行时 WebSocket/MQTT 选择与回退：需要 OTA 响应，`NOT RUN`；
- 实机：硬件测试中心当前只有 matrix/corep4/sticks3/stopwatch，无 CoreS3/StackChan，
  `NOT RUN`；
- 第二台设备与 100 ms 配置：`NOT RUN`。

## 9. 风险与回滚

本次评审只读，没有修改上游仓库、没有 push、没有关闭 PR。记录内所有会话已在本地 Device Service
停止；未保留虚拟 flash。构建目录为临时目录，可随时删除。

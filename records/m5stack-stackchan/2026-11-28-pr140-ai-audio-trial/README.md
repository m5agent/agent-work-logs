# StackChan #140 评审：AI.AGENT 语音播放的可选试验（WebSocket + 80 ms I2S）

- 日期：`2026-11-28`
- 结果：`PARTIAL`（`build` 与有限的 `virtual-device validation` 通过；语音质量、实机与
  WebSocket/MQTT 运行时对照 `NOT RUN`）
- 工作类型：`pr_review`
- 问题来源：[m5stack/StackChan#140](https://github.com/m5stack/StackChan/pull/140)，
  作者 `pkh31337`，英文，OPEN；评审前无评论
- 源码版本：`m5stack/StackChan` base `28b9f0c`（v1.6.2），PR head `30820d66`；
  依赖 pin `78/xiaozhi-esp32` `49b4380b`（v2.5.2）
- 环境：macOS arm64；ESP-IDF v6.1；本机 Device Service 的 `stackchan` profile
  （ESP32-S3 虚拟设备，qemu 运行时）。没有 StackChan/CoreS3 实机

## 结论

补丁与描述一致，未发现阻塞问题：Kconfig 选项默认关闭且只对 StackChan 板生效，patch 能干净地
应用到 pin 的 xiaozhi-esp32 v2.5.2，两种配置都能用 ESP-IDF v6.1 构建；试验版在虚拟 StackChan
上完成启动并打开 AI.AGENT，`CoreS3AudioCodec` 以 8 个 DMA descriptor 初始化成功。默认关闭时
静态尺寸与打开时完全相同，额外开销只发生在运行时。

两个值得写进评审的事实：

1. 内存代价可以量化：按 IDF v6.1 的 DMA 分配公式，两个方向各多 2 个 descriptor，
   TX 每 descriptor 960 B、RX 1920 B，合计 **+5760 B 内部 DMA RAM**；虚拟设备上同一路径
   codec 初始化后的 free SRAM 为 70495 B（试验）对 76407 B（原版），差值 5912 B，与计算一致。
2. 试验版在 OTA 同时给出 MQTT 和 WebSocket 时总是选 WebSocket；如果网络只放行 MQTT，
   设备会落到 WebSocket 错误路径，而不是原版的 MQTT 回退。这是作者已声明的试验行为，
   但测试者需要知道它看起来像回退。

## 关键证据

- patch：`git apply --check` 首次通过、第二次按预期失败、`--reverse --check` 通过，
  即仓库的 fetch 辅助脚本会识别“已应用”。
- 构建：`build-off` 与 `build-on` 均 `exit 0`；`build-on/config/sdkconfig.h` 有
  `CONFIG_STACKCHAN_AI_AUDIO_TRIAL 1`，`build-off` 没有；两者 Flash Code 2676904、
  DIRAM 207868 完全相同。
- 代码生成：`CoreS3AudioCodec::CreateDuplexChannels` 的 `dma_desc_num` 存储立即数从 6
  变为 8（objdump，栈偏移 172）。
- 虚拟设备：`stackchan`（qemu），试验镜像 SHA-256
  `251eb220…df487`；启动后经 welcome Skip → launcher → AI.AGENT，串口出现
  `CoreS3AudioCodec initialized` / `Audio codec started` 与 ES7210 TDM 输入使能，
  未出现 I2S 初始化错误。
- 语义核对：`PushPacketToDecodeQueue(packet, true)` 的等待条件包含 service stop 与
  playback generation 变化（`audio_service.cc:609-627`），且 `Stop()`/`ResetDecoder()`
  在持锁时递增 generation 并 `notify_all()`，因此停止/中断不会永久挂住。

## 文件

- `report.md`：完整评审、源码行号、构建与虚拟设备过程
- `run.json`：结构化记录
- `evidence/pr140.diff`：被评审的 3 文件 diff
- `evidence/patch-apply.txt`：patch 应用与幂等检查
- `evidence/build-summary.txt`：两种配置的构建、镜像哈希与静态尺寸
- `evidence/objdump-dma-desc.txt`：6→8 descriptor 的机器码证据
- `evidence/sessions-summary.json`：两次虚拟设备会话的关键字段
- `evidence/serial-trial-redacted.log` / `serial-stock-redacted.log`：串口原文（MAC 已脱敏）
- `evidence/frame-*.png`：虚拟设备画面

## 未覆盖项

- 语音是否仍断字、I2S underrun/drop、首音时延、打断时延、唤醒词与重连：没有 StackChan
  服务端音频流，全部 `NOT RUN`；
- WebSocket/MQTT 的运行时选择与回退：没有 OTA 响应，`NOT RUN`（仅代码级核对）；
- 实机：本机硬件测试中心当前只有 matrix/corep4/sticks3/stopwatch，无 CoreS3/StackChan，
  `NOT RUN`；
- 第二台设备、100 ms 配置、内部内存压力复现：`NOT RUN`。

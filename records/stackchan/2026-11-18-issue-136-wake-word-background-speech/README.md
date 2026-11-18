# StackChan Issue #136 非唤醒激活与背景语音延长对话

- 日期：`2026-11-18`
- 结果：`REVIEW`
- 工作类型：`issue`
- 问题来源：https://github.com/m5stack/StackChan/issues/136
- GitHub 回复：https://github.com/m5stack/StackChan/issues/136#issuecomment-6969507194
- 源码版本：`m5stack/StackChan @ 94856a7`（v1.6.0）；对照 `28b9f0c` / `0808a47`（v1.6.2）；`78/xiaozhi-esp32 @ v2.2.4`、`v2.5.2`
- 环境：macOS，源码只读检视；无 ESP-IDF 6.1 工具链；未连接实机

## 结论

报告描述的两类现象与 V1.6.0 AI.AGENT 音频链路的两处实现一致，而不是单一唤醒词缺陷：
唤醒词使用固定的预训练 WakeNet 模型（灵敏度不可由用户配置，唤醒音频也不上传服务端校验）；
服务端 `tts stop` 后设备自动回到 Listening，Listening 期间不再需要唤醒词且没有设备侧超时，
因此一次误唤醒可以因电视语音被当作后续对话而持续多轮。V1.6.2 升级到 xiaozhi v2.5.2 /
esp-sr 2.4.7 / WN9L 模型，但 `tts stop` 后自动重听逻辑未变，未发现可证明降低误唤醒率的证据。
结论为源码级验证，运行与实机层级均未执行。

## 关键证据

- 源码：`firmware/repos.json`（v1.6.0 使用 xiaozhi v2.2.4）、`firmware/sdkconfig.defaults:15-16`
  （`CONFIG_SEND_WAKE_WORD_DATA=n`、`CONFIG_SR_WN_WN9_HISTACKCHAN_TTS3=y`）。
- xiaozhi v2.2.4 `main/application.cc:531-539`：`tts stop` 后非 ManualStop 模式一律回到 Listening；
  `:950-951` 默认模式由 AEC 开关决定；`:708-709` Listening 状态下点击屏幕关闭音频通道。
- xiaozhi v2.2.4 `main/audio/wake_words/afe_wake_word.cc:73-75`：AFE 以固定配置初始化，
  AEC 使用 ES7210 参考通道；无用户阈值入口。
- 设备端设置只有空闲动作频率与空闲自动关机（`firmware/main/apps/app_setup/workers/ai_agent.cpp`），
  无唤醒灵敏度或对话超时项。
- v1.6.2 差异：xiaozhi 2.2.4 → 2.5.2、esp-sr 2.3.0 → 2.4.7、WN9 → WN9L；2.5.2 的
  `application.cc:629-638` 仍为 `tts stop` 后回到 Listening。

## 文件

- `report.md`：完整分析、代码位置与限制
- `run.json`：结构化记录
- `evidence/01-v160-manifest.txt`：V1.6.0 依赖与唤醒配置
- `evidence/02-xiaozhi-v224-audio-path.txt`：xiaozhi v2.2.4 唤醒/状态机代码摘录
- `evidence/03-v162-delta.txt`：V1.6.2 相关差异
- `evidence/04-settings-and-touch.txt`：设备设置项与触摸映射
- `evidence/05-device-service-profile-summary.json`：本机虚拟设备 profile 摘要（设备标识已移除）
- `evidence/06-reply.md`：GitHub 回复原文

## 未覆盖项

- 实机 `NOT RUN`：无设备访问，且需要绑定账号与真实 AI 服务会话才能复现对话链路。
- 虚拟设备 `NOT RUN`：本地有 StackChan QEMU profile（显示/触摸/Wi-Fi 与 ES7210 模型），
  但 AI.AGENT 需要已绑定设备与在线服务会话；误唤醒率还取决于用户房间内的真实电视音频，
  合成 PCM 无法给出该统计结论。
- 构建 `NOT RUN`：本机未安装 ESP-IDF 6.1，也未拉取 xiaozhi 依赖。
- 服务端超时 `NOT RUN`：服务端不在本仓库，无法确认关闭音频通道的具体时长。

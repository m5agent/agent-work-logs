# StackChan Issue #136：非唤醒激活与背景语音延长对话（源码级分析）

## 1. 问题来源与现象

- 条目：https://github.com/m5stack/StackChan/issues/136（作者 minimalistbuilderhq，OPEN，此前无评论）
- 环境（作者自述）：StackChan 实机、Factory V1.6.0、AI.AGENT 模式、英文
- 现象：设备会在没有明确唤醒的情况下发起对话；会把电视对白或人与人对话当作对它的语音；
  未得到回应仍反复追问；一次持续数分钟；口头表示结束对话后仍响应电视语音
- 作者诉求：确认是否为 V1.6.0 已知问题；唤醒灵敏度/对话超时/重新激活是否可配置；
  是否有官方推荐的电视误触发规避方式；是否有不要求自定义固件的改进计划

## 2. 分析范围与判定

条目语言为英文，结论按英文发布。工作只做源码核对，不修改仓库、不关闭条目。

V1.6.0 的 AI.AGENT 不是 M5Stack 自研语音栈，而是集成 xiaozhi-esp32：`firmware/repos.json`
在该版本指向 `v2.2.4`，并通过 `patches/xiaozhi-esp32.patch` 注入 StackChan 的板级差异
（音频 codec 参数、OTA、视频等）。因此运行时行为需要按 xiaozhi v2.2.4 的状态机核对。

## 3. 发现

### F1. 唤醒词是固定模型，无用户灵敏度配置

`firmware/sdkconfig.defaults:15-16`：

```
CONFIG_SEND_WAKE_WORD_DATA=n
CONFIG_SR_WN_WN9_HISTACKCHAN_TTS3=y
```

板级 `firmware/main/hal/board/config.h:8` 设 `AUDIO_INPUT_REFERENCE true`，
`stackchan.cc` 以 ES7210 双通道（麦克风 + 参考）构造 `CoreS3AudioCodec`。

xiaozhi v2.2.4 `main/audio/wake_words/afe_wake_word.cc:73-75`：

```c
afe_config_t* afe_config = afe_config_init(input_format.c_str(), models_, AFE_TYPE_SR, AFE_MODE_HIGH_PERF);
afe_config->aec_init = codec_->input_reference();
afe_config->aec_mode = AEC_MODE_SR_HIGH_PERF;
```

检测门限由 esp-sr 模型/AFE 默认值决定，代码中没有从设置读取阈值或灵敏度的路径。
`CONFIG_SEND_WAKE_WORD_DATA=n` 意味着唤醒词音频不会作为会话首包上传，服务端只能收到
唤醒后的麦克风音频，无法复核这次唤醒是否真的是唤醒词。

### F2. `tts stop` 后自动回到 Listening，形成可延续的多轮

xiaozhi v2.2.4 `main/application.cc:531-539`：

```c
} else if (strcmp(state->valuestring, "stop") == 0) {
    Schedule([this]() {
        if (GetDeviceState() == kDeviceStateSpeaking) {
            if (listening_mode_ == kListeningModeManualStop) {
                SetDeviceState(kDeviceStateIdle);
            } else {
                SetDeviceState(kDeviceStateListening);
            }
        }
    });
```

`main/application.cc:950-951` 决定默认模式：

```c
ListeningMode Application::GetDefaultListeningMode() const {
    return aec_mode_ == kAecOff ? kListeningModeAutoStop : kListeningModeRealtime;
}
```

StackChan 未启用 `CONFIG_USE_DEVICE_AEC`（该选项的 depends 列表也不含
`BOARD_TYPE_M5STACK_STACK_CHAN`），所以默认是 AutoStop；除 ManualStop 外，
每次 TTS 结束都直接回到 Listening。

Listening 期间唤醒词检测默认关闭（`main/Kconfig.projbuild:732-740`，`default n`），
即麦克风音频不再经过唤醒词门控，直接作为下一轮用户语音；设备端没有固定的 Listening
超时定时器（`application.cc` 中只有状态栏时钟与空闲省电定时器）。回到待机依赖服务端关闭
音频通道（或用户操作/错误路径）。因此一次误唤醒即可形成：

```
误唤醒 -> 回复 -> 自动 Listening -> 电视语音被当成追问 -> 回复 -> 自动 Listening -> ...
```

这与“未得到回应仍追问”“持续数分钟”“说结束之后又响应”三项观察一致。

### F3. 口头“结束对话”不是设备端命令

设备只在收到服务端 `tts stop`、音频通道关闭、或用户在 Listening 状态下点击屏幕时改变状态
（`application.cc:708-709` 调用 `CloseAudioChannel()`）。LLM 说“结束对话”只是 TTS 文本，
不会触发协议层关闭。StackChan 的屏幕点击到 `ToggleChatState()` 的映射见
`firmware/main/hal/board/stackchan_display.cc:256-266`。

### F4. 可配置项只有空闲动作与空闲关机

`firmware/main/apps/app_setup/app_setup.cpp:61-92` 的 Device 菜单为 Brightness / Volume /
Timezone；AI.Agent 菜单只有 General（Idle movement frequency）与 Power Saving
（Automatically power off after being idle for）。`ai_agent.cpp` 持久化字段为
`idleShutdownTimeSeconds`、`allowShutdownWhenCharging`、`idleRandomMovementLevel`。
没有唤醒灵敏度、对话超时或“单轮/连续对话”开关。

### F5. V1.6.2 的变化不足以宣称修复

`git diff 94856a7 0808a47 -- firmware`：

- `firmware/repos.json`：xiaozhi `v2.2.4` → `v2.5.2`
- `firmware/main/idf_component.yml`：`espressif/esp-sr ~2.3.0` → `==2.4.7`
- `firmware/sdkconfig.defaults`：`CONFIG_SR_WN_WN9_HISTACKCHAN_TTS3` → `CONFIG_SR_WN_WN9L_HISTACKCHAN_TTS3`

xiaozhi v2.5.2 的 `main/application.cc:629-638` 仍是 `tts stop` 后非 ManualStop 回到
Listening，`:1183-1190` 的默认模式逻辑未变。WN9L 与 WN9 的误接受率差异没有公开量化数据，
本记录不把 v1.6.2 表述为对该现象的修复。

## 4. 执行过程

```bash
# 源码与版本
git clone --depth 50 https://github.com/m5stack/StackChan /tmp/stackchan-136
git -C /tmp/stackchan-136 show 94856a7:firmware/repos.json
git -C /tmp/stackchan-136 show 94856a7:firmware/sdkconfig.defaults
git -C /tmp/stackchan-136 diff 94856a7 0808a47 -- firmware

# 上游基线
git clone --depth 1 --branch v2.2.4 https://github.com/78/xiaozhi-esp32 /tmp/xz-v2.2.4
git clone --depth 1 --branch v2.5.2 https://github.com/78/xiaozhi-esp32 /tmp/xz-v2.5.2

# 本机虚拟设备 profile（只读查询，未创建会话）
# GET /api/v1/devices 过滤 stackchan
```

除上述命令外没有构建、烧录或运行。Device Service 仅用于确认 StackChan profile 存在及其
能力边界，未创建会话、未注入 PCM。

## 5. 为什么没有使用虚拟设备验证

本机 Device Service 存在 StackChan profile（QEMU `m5stackchan`，ILI9342 320×240 触摸屏，
Wi-Fi 已验证，外设含 ES7210/AW88298 等），但本条目无法用该 profile 形成有效证据：

1. AI.AGENT 的对话链路需要设备已完成激活/绑定并连接在线 AI 服务；模拟器没有该服务会话，
   无法复现“回复后自动重听、电视语音被当成追问”的闭环。
2. 误唤醒是固定声学模型对用户房间内真实电视音频的统计行为；模拟器只能注入确定性 PCM
   片段，不能据此给出误接受率，也不能证明或排除用户遇到的那次触发。
3. 本机没有 ESP-IDF 6.1 与 `fetch_repos.py` 拉取的 xiaozhi 依赖，未构建 factory 镜像；
   仓库 README 也说明公开源码可能落后于已发布固件。

因此本记录只声明 code-level verification，不声明 virtual-device validation。

## 6. 未覆盖项与风险

- 实机、虚拟设备、构建、烧录：`NOT RUN`（原因见上）。
- 服务端何时关闭音频通道、是否存在服务端 VAD 超时：`NOT RUN`，服务端不在本仓库。
- 无法确认 M5Stack 是否已将该现象登记为缺陷；无法给出改进排期。
- 公开源码与 factory 镜像可能存在细节差异（README 明确说明更新可能滞后）。
- 若作者能提供一次事件前后的 USB 串口日志（`Wake word detected: ...` 与随后的 `tts`/`stt`
  消息），可区分“新的误唤醒”与“自动 Listening 窗口”，这是目前缺失的关键证据。

## 7. 回复策略

按条目语言用英文发布一条评论：结论 → 证据等级（code-level verification）→ 代码位置 →
可配置项与可行的非自定义固件缓解 → 未覆盖项与所需信息。不关闭条目、不 push、不改他人仓库。

## 8. 发布结果

- 2026-11-18T04:57:21Z 在 issue #136 发布唯一一条英文评论（评论 id 6969507194）：
  https://github.com/m5stack/StackChan/issues/136#issuecomment-6969507194
- 评论内容见 `evidence/06-reply.md`；未关闭条目、未 push 代码、未修改他人仓库。

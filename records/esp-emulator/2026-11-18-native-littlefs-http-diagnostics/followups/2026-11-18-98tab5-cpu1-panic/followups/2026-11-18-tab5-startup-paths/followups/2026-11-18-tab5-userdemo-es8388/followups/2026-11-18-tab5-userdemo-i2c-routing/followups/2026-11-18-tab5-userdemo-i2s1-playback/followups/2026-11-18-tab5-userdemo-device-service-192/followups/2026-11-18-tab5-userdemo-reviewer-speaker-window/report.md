# Tab5 UserDemo 触控动作的数字音频取证

[前一里程碑](../../report.md)验证了 UserDemo V0.4 在 1.92.0 停机后可读到虚拟 I²S1 PCM，同长空闲对照在动作标记后全为零。本次为 Reviewer 增加可经 HTTP 复核的标记与证据范围。

## 接口与证据绑定

录音仍由 `speaker_capture: true` 开启，租约最长 180 秒且不可续期。对具备能力的工作端，正在运行的 Tab5 录音可从 `audio.pcm?format=cursor` 取得四字节对齐的有效字节数和录音标识。原生后端运行中先保留 44 字节全零的 WAV 头，游标按文件增长观察有效字节数。停机前只能观察游标。停止并保留历史后，使用相同的 `expected_recording_id` 读取指定范围的 PCM 和指标。录音标识随会话重置而变化，已保留的录音在服务重启后维持同一标识。

同一会话的证据 ZIP 支持最多 1 MiB 精确 PCM 窗口。其清单绑定录音标识、起止偏移、文件摘要和全录音观察字节数。旧标识、超出末尾的范围和缺失有效读权限都会拒绝。测试覆盖了从原先默认前 8 MiB 以外读取局部范围。原有 Cardputer 和 Dial 单声道路径继续通过原有测试。

## 早期对照与判定修正

首轮试验缺少完整运行时资源，审核在设备执行前退出。第二轮在两份同一原版的来宾上复现游标拒绝，HTTP 409 阻止了触控证据。两个来宾的 WAV 在运行中增长，停机前保留全零占位头。修复后游标可以绑定同一代录音。[两个运行中 WAV 的占位头记录](evidence/native-live-wav-header.summary.json)

第三轮按动作后的首个 1 秒判定，播放组和对照组都给出音频断言 PASS。对同会话 ZIP 的原始 PCM 以 100 毫秒区间重算双声道 RMS 后，对照组的非零值集中在动作标记后 0.3–0.5 秒，之后到 1.0 秒采样全为零。播放组在 0.3–1.0 秒连续活动。对照触控触发的来宾界面短声因此能通过原阈值。两条任务整体仍为 `manual_review E_NETWORK_PARTIAL`。[早期对照及 PCM 复核](evidence/early-controls.summary.json)

## 精确冻结包和同固件对照

选定实际触控后，证据 ZIP 保存按同一录音标识对齐的 400,384 字节。首先保留触控前最后 4,096 帧用于安静基线，接着保留触控后的两段各 48,000 帧。评估排除第一秒的界面短声，使用第二秒的左右声道 RMS 判定持续播放。两组的触控前 RMS 都是零，指定区域均按预期变化，每个真实 GT911 触控均收到 7/7 条报告。

| 同一原版固件与隔离 Reviewer 保存快照 | Music Test → Play | 仅打开 Music Test |
| --- | ---: | ---: |
| 触控后第一秒非零 s16le 样本 | 67,514 | 9,598 |
| 触控后第二秒非零 s16le 样本 | 95,995 | 0 |
| 第二秒左、右声道 RMS | 3713.650、4601.958 | 0、0 |
| 音频断言 | PASS | PARTIAL |
| 整体审核结果 | manual_review · E_NETWORK_PARTIAL | manual_review · E_TAB5_SPEAKER_PARTIAL |

最终冻结包使用 Device Service 源码 `8ba3677708fbf11d47576f2dda1baa8431492452`，Reviewer 源码 `aebbe38ce0fa2ba5c278270554ef8af6f5da8a32`。两个 ZIP 的 CRC、清单和文件 SHA 均通过回读，并绑定同一会话、同代录音和原版固件。测试保留了会话历史、释放 Flash、退出隔离服务，活动租约归零。较早的 A4 冻结前验证给出相同分类。[最终冻结包证据](evidence/final-frozen-reviewer.summary.json) · [隔离原版 A4 双对照](evidence/reviewer-a4.summary.json) · [Device Service 平台回归](evidence/platform-c6d7e.summary.json)

设备服务与审核源码的主分支和常驻合同均已核对。常驻回读设备服务 1.93.0 与 Reviewer 0.23.0，最终文档检查通过 51 项。上表依据精确冻结包的来宾执行。[Device Service API](https://github.com/m5agent/m5stack-esp-emulator/blob/8ba3677708fbf11d47576f2dda1baa8431492452/docs/device-service-api.md#tab5-userdemo-i2s1-speaker-output)

## 范围

数字音频结果依赖已配置的精确 UserDemo V0.4 固件、GT911/ILI9881C 原生板型和指定触控计划。浏览器、实体音频及模拟电气测量均为 NOT RUN。未提交 Burner。

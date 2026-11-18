# 原版 Tab5 UserDemo 采集会话复位验证

在冻结 Device Service 1.92.0 中导入同一原版 UserDemo V0.4。Tab5 以固定
esp-emu、GT911 Codec Part 及原始应用字节启动。通过 `POST /api/v1/sessions`
创建 `speaker_capture=true` 的 120 秒录制会话，等待原生 I2S1 产生采集
文件数据。两代来宾运行时，`GET /api/v1/sessions/{id}/audio.pcm` 都返回
`409 audio_capture_pending`。首次运行中的 WAV 尚未写入最终 RIFF 头。

通过 `POST /api/v1/sessions/{id}/reset` 复位。旧文件的只读描述符仍可访问，
路径已解除链接，文件的最终 PCM 为 385,344 字节。解析后的新 WAV 对应不同
inode 和新的 P4 进程。复位保留会话和原租约到期时间。串口记录新的
`ESP-ROM:esp32p4` 启动标记，同会话记录 `reset` 事件并取得新的 720 × 1280
原生 DSI 非黑帧。

停机保留会话历史，释放可写 Flash。新一代最终 WAV 为 48 kHz、16 位双声道。
256,704 字节的 PCM 与旧一代哈希不同。以 4,096 字节范围回读 HTTP 二进制和
metrics，两者哈希与新 WAV 对应范围一致。同会话 ZIP 的 `audio/speaker.pcm`
与新 WAV 的完整 PCM 一致，六个清单成员均校验，活动租约为零。
[原版、运行时和证据哈希](evidence/reset-lifecycle.summary.json)

本轮覆盖一次显式 API 复位、文件更换和停机后回读。播放操作、由来宾自行触发
的复位、实体音频和 Burner 提交未执行。 [固定 Device Service 源码](https://github.com/m5agent/m5stack-esp-emulator/commit/1c2eb72d3b7e517e2ceb487c408708a5b800a8c8)

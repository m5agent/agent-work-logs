# 实施与验证

此前的原版 UserDemo V0.4 已能播放音乐并通过真实 I²S1 TX 取证。接收端一直
没有向 Device Service 的标准会话接口开放。官方 esp-emu 1.1.0 同一 I²S
实例已支持从 WAV 供给接收端。新增会话字段绑定内容寻址 WAV，验证 RIFF、
实际位宽、48 kHz 四槽格式、文件长度和权限后，将会话私有副本只接到原生 P4
I²S1。C6 不接收音源。服务在重启 P4 前复核该副本。回执与证据清单保存源
文件及 PCM 摘要。输入到达应用由实际画面和独立的输出观测证明。
[运行时命令契约](https://github.com/espressif/esp-emulator/blob/v1.1.0/docs/guides/CLI.md)

## 可复验路径

源版本为 `1d77f11b521b4521276d44dde0c1ecb0e8596741`。固定原版 UserDemo V0.4
`2d30fa8918bac1e8d09b59eb2fc72ea40500d097efa4812e241ac875ee86e781`、
规范化 Flash `62a86dd0ec80b98f443e1e43aea28e3517ef6877b5c339d111f897a8cc55e9c9`、
esp-emu 1.1.0 `633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828`、
GT911 codec Part `2505106410b2f6b18b2ad243bc4c3730961762710ea565733fe7a8b117387270`。
配置该 Flash 的 GT911/ILI9881C 原生 DSI 准入，不上传 ELF。请求经普通
Device Service HTTP API，最终对照没有附加启动适配器。

以下生成 10 秒合成信号。左麦位于槽 0，右麦位于槽 2，另两槽静音。

```python
import math
import struct
import wave

period = b"".join(
    struct.pack("<hhhh",
                round(12500 * math.sin(2 * math.pi * 440 * i / 48000)), 0,
                round(16500 * math.sin(2 * math.pi * 880 * i / 48000)), 0)
    for i in range(1200)
)
with wave.open("microphone.wav", "wb") as fixture:
    fixture.setparams((4, 2, 48000, 0, "NONE", "not compressed"))
    fixture.writeframes(period * 400)
```

通过 `POST /api/v1/artifacts` 上传原版 BIN 和 WAV，经 `/firmware/import`
导入固件。为 `device_id=tab5` 和 `runtime=qemu` 创建离线会话，传入
`microphone_wav_artifact_id` 和 `speaker_capture: true`。等待原版桌面，
用面板坐标 (49,793) 进入双麦测试，点 (143,587) 开始录音。用新帧识别菜单
波形及 REC、PLAY、IDLE，在各阶段同时读 I²S1 TX 游标。停止来宾后按同一
录音标识读取 PCM 和有界 ZIP，比较 PLAY 窗口的信号与输入频率。将 PCM 换成
等长度的全零数据即可复验静音。重复会话设备复位后，核对原源文件、PCM 摘要、
新录音代和实际录放结果。原版串口没有可用的录音状态文字，帧与 PCM 是验收依据。

## 实测与范围

- 最终版 tone 在 PLAY 区间取得 29 个有信号的 100 ms 窗。左 440 Hz 和右
  880 Hz 的各自峰值约 10,837 和 11,711。所测是数字回放频率和声道，
  早期样本未发现与夹具完全相同的长字节序列。
- 静音对照两波形跨度为零，REC 到 IDLE 期间的 PCM 全为零。早期一次仅保留
  可见波形及无原版串口状态的 PARTIAL 样本，随后使用实际帧与游标完成验收。
- 普通 HTTP 下双声道 WAV 返回 400，缺少 `audio.inject` 返回 403，均没有
  分配租约或启动来宾。最终解析器另拒绝截短文件和非 16 位头，原版同输入复验
  继续通过。
- 各运行绑定固件、Part、运行时、帧、回执和 ZIP。结束后租约归零，P4/C6
  与隔离服务均退出。原始 ZIP、录音、画面与本地运行位置保留在私有材料。
- 真机声学、浏览器、其他板型及其他固件为 NOT RUN。Burner 未提交。

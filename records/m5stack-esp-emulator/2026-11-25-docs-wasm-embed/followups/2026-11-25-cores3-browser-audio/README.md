# CoreS3 文档例程浏览器音频

- 日期 2026-11-25
- 结果 **PARTIAL**。原始 Arduino WAV 和 UIFlow2 麦克风例程通过隔离 Chromium WASM 预览和 0048 完整源码构建的数字音频验证。
- 工作类型 Issue 修复与虚拟设备验证
- 环境 ESP32-S3 CoreS3，源码构建的 QEMU，Emscripten 3.1.50，Chromium
- 问题来源 [Issue #248](https://github.com/m5agent/m5stack-esp-emulator/issues/248)

勾选播放后，用工作台原有的上传或编辑器流程即可运行两条例程。按实际 Start 手势打开的 48 kHz AudioContext 接收 I²S1 和 GDMA 取出的数字音频。Arduino WAV 的原固件音量较低。UIFlow2 麦克风使用固定的 440 Hz 虚拟输入。

| 原始例程 | 浏览器证据 |
| --- | --- |
| Arduino WAV | 匹配的 microSD、320×240 中出现 12 帧不同画面，以及 575,037 个非零输出采样 |
| UIFlow2 v2.5.3 麦克风 | 实际导入和运行，从录制、播放到完成的原始画面，119,996 个非零输出采样，以及已确认的编辑器中断 |

两次运行均由实际停止操作关闭浏览器音频上下文，QEMU 正常退出。所测窗口内队列丢弃和欠载均为零，六个 Worker 全部退出。

[报告](report.md) · [结构化记录](run.json) · [复跑步骤](code/replay.md) · [最终浏览器摘要](evidence/browser-audio.summary.json) · [描述符对照](evidence/i2s-pacing.summary.json)

[0048 完整构建复测](follow-up-locked-0048.md) · [完整构建执行记录](follow-up-locked-0048.run.json) · [Speaker 资源待验收项](speaker-follow-up.md)

UIFlow2 Speaker 原例程的音频素材使用范围及浏览器装配单独跟踪。生产部署、文档嵌入、真机声学和其他浏览器尚未验收。[Speaker 素材 #271](https://github.com/m5agent/m5stack-esp-emulator/issues/271)

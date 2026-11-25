# CoreS3 浏览器 I²S 文件播放及录放诊断

- 日期 2026-11-25
- 类型 diagnosis，virtual-device validation
- 设备 CoreS3，浏览器 WASM
- 问题 [模拟器 #248](https://github.com/m5agent/m5stack-esp-emulator/issues/248)

用相同的 WASM 和原程序区分 I²S 完成中断、控制器 PCM 与浏览器发声。默认 Arduino SD WAV 在首段复现停滞。隔离诊断配置使 I²S DMA 交付完整的有效 PCM，且两份原程序正常停止。工作台实时节拍、可听输出和原 Speaker 素材仍待处理。

- [范围、对照和复现](report.md)
- [结构化记录](run.json)
- [原 Arduino WAV 与 PCM 对照](evidence/arduino-wav.summary.json)
- [原 UIFlow2 Microphone 控制器与 LCD](evidence/uiflow-mic.summary.json)

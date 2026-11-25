# CoreS3 UIFlow2 Speaker 原始资源验收

保留原始 Speaker 例程独立跟踪。程序在启动和点击其 Play 图形后都尝试打开 /flash/res/audio/poweron_2_5s.wav。原始 Python SHA-256 为 ec7f07036410d52e87ad801dc36b861802d28daa2d05bb320326a399fc1f7273。

已定位的上游音频 SHA-256 为 07f0d5ad0bac7bdca38388c52e6daf9042811c7a5cd5c36f1c383be4b236f14c，大小 441,538 字节，格式为 44.1 kHz 立体声 signed 16-bit PCM。其元数据署名 Sound Ideas。上线前由资源权利方确认允许的分发或授权提供路径。当前音频工作台导出不附带该文件。

验收时取得允许使用的原始文件，单独按摘要校验。将其挂入同一工作台 guest 的原始文件路径。现有组合器固定写入 Python 启动路径并限制单文件为 256 KiB，需要为该例程实现限定范围的资源导入。用原始 v2.5.3 环境和原始程序验证启动播放、按下和释放 Play 区域后的第二次有声数字流、实际 I²S TX 格式、工作台中断及清理。如果使用自行生成的音频替代，记录为另一项改编示例验收。

[原始例程固定源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/hardware/speaker/cores3_speaker_example.py) · [资源方许可说明](https://sound-ideas.com/pages/sound-ideas-end-user-license-agreement) · [浏览器音频总问题 #248](https://github.com/m5agent/m5stack-esp-emulator/issues/248)

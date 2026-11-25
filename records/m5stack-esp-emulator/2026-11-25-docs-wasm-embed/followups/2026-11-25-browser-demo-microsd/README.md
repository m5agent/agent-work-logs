# CoreS3 与 Cardputer-Adv 文档例程 microSD 挂载

- 日期 2026-11-25
- 工作类型 fix，virtual-device validation
- 设备 CoreS3、Cardputer-Adv，Chrome 158.0.8127.37
- 问题来源 [模拟器 #253](https://github.com/m5agent/m5stack-esp-emulator/issues/253)
- 源码基线 `176ecd7b28ed1e3b506c6d6f8b0bbc1c05293463`，候选 `5a61d685e82c73f438c991e32d2acfdb4afe689a`
- 音频、物理卡和正式托管未执行

CoreS3 原始 SDcard 与 Picture 从工作台读取并显示两张卡载样例图。Cardputer-Adv 原始 8 MiB SDcard 例程完成文件改名、28 字节读取和 1 MiB 写入。两次启动各得到初始卡内容。无卡和损坏 gzip 对照分别观察到原程序缺卡提示及启动前素材错误。实际会话正常退出并回收 Worker。

CoreS3 原版 WAV 打开素材，读到文件头及第一个数据段。播放进度和音频留在 [#248](https://github.com/m5agent/m5stack-esp-emulator/issues/248)。

- [项目背景、复现和验证范围](report.md)
- [结构化执行结果](run.json)
- [初始工作台矩阵及重复启动](evidence/initial-matrix.summary.json)
- [最终工作台矩阵及对照](evidence/final-matrix.summary.json)
- [独立实际 SPI 读写证据](evidence/cores3-spi-trace.summary.json)
- [原版 WAV 文件读取](evidence/wav-file-read.summary.json)

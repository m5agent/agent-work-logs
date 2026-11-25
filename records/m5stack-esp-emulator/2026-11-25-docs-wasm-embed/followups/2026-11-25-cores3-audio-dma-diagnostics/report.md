# 浏览器虚拟设备执行

固定 Xtensa WASM `e350ed7b2f969139803befef12757178049427058a212136868d382dfe5a5f4b`。对照使用标准工作台，诊断导出仅改其 Worker 的启动环境和有界 MEMFS 输出。原固件、客体代码与控制器模型保持相同。用 `M5SW_I2S_DMA_IRQ` 打开现有完成中断和描述符路径，同时设置 PCM 文件输入或输出，用实际 I²S1 DMA 事件及文件数据验算。

| 程序 | 虚拟设备证据 |
| --- | --- |
| Arduino 卡载 WAV | 标准路径加载同一会话 microSD，读到 16 kHz 单声道 PCM 的 WAV 文件头，36 秒内屏幕仍为 Segment 1、约 4.3%。 |
| Arduino 卡载 WAV，诊断 | 同一 WAV 原例程实际完成 2,561 条 TX 描述符。24 个有效音频段共 576,000 个 48 kHz 单声道采样。逐段对应同源 16 kHz WAV，归一化相关系数最低 0.99999474，末尾有 53 个静音描述符。当前每次调度约 20 ms，单条 512 字节只含 5.33 ms 音频。 |
| UIFlow2 Microphone，诊断 | 原 Python 显示 `rec... → play... → done`。固定 16 kHz、440 Hz 虚拟 PCM 经 RX DMA 177 次交付，共 90,112 字节。I²S1 TX 又采到对应约 440 Hz 的回放。编辑器中断收到原客体回执，随后正常退出。 |

浏览器通过原工作台 Start 和 Stop，所有被测会话退出码 0，6 个 Worker 全部回收。PCM 从虚拟 DMA 捕获。浏览器输出设备、实际声压、物理麦克风、正式托管和原 Speaker 精确素材完整播放未执行。

## 独立复现

1. 使用 [0043 锁定构建记录](../2026-11-25-cores3-qvga-camera/evidence/locked-build.summary.json) 的 WASM 和 CoreS3 ROM，按标准工作台导出。
2. 以 [microSD 记录](../2026-11-25-browser-demo-microsd/) 的原 Arduino 卡载 WAV 固件和 16 kHz 种子镜像运行标准工作台，核对固件、种子和帧摘要。对照保留至少 36 秒。
3. 单独导出本地诊断副本，在调用原 QEMU 前的 Worker `preRun` 设置 `M5SW_I2S_DMA_IRQ=1`，把 `M5SW_I2S_PCM_FILE` 指到会话私有、容量有界的 MEMFS 输出，打开现有 I²S 描述符跟踪。重复同一固件和种子。读取 DMA 描述符计数、截断前 PCM 与实际客体画面，核对起止及静音段。
4. 在另一个实际工作台会话启动 UIFlow2 v2.5.3，导入并执行 [CoreS3 Microphone 原例程](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/hardware/mic/cores3_mic_example.py)。诊断副本额外把 `M5SW_I2S_RX_PCM_FILE` 指到摘要匹配的 16 kHz 单声道 s16le 440 Hz 合成信号。核对原例程的三个画面里程碑、真实 RX 和回放 TX。通过编辑器中断并正常停止。

设备模型需进一步依据 I²S 寄存器和描述符长度计算播放节拍。对外工作台还需拥有可停止的浏览器音频输出。Speaker Python 依赖原始 `poweron_2_5s.wav`，该文件记录有第三方音效出版者信息。本记录保留原问题和验证方法，不分发该素材。

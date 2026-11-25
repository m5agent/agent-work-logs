# CoreS3 浏览器 I²S 音频验证

## 复现和修复

原始 Arduino 固件和匹配的示例 microSD 已校验。基线有卡时进入播放画面，第一段停在 4.3%。C 诊断启用已有 DMA 完成 IRQ 后可以取得真实 PCM，但 512 字节描述符的旧定时约为 20.24 ms。该文档固件实际配置 I²S1 标准模式、48 kHz 和单声道 signed 16-bit，描述符时长为 5.333 ms。按实际声道与采样率修正定时后，原固件的同一路径在诊断中读出完整输入的 24 段播放，源波形最低分段相关系数 0.9999947。配套摘要分别保留宿主时间和虚拟时间。

预览使用已有的 GDMA 描述符完成路径。实际完成的 PCM 由固定字符设备送入每个会话各自的 8,192 采样缓冲区，再由标准 AudioWorklet 输出。原文件取证约 4 MiB 的限制与播放缓冲区独立。开始前须明确勾选，AudioContext 在 Start 的用户手势内恢复。正常停止关闭上下文，状态切换清理缓冲数据。

第一次浏览器 WAV 复跑因测试阈值高于原例程音量而记为 FAIL。第一次麦克风复跑出现非零浏览器 PCM 和实际播放画面，但有符号 HEAP8 的低字节发生符号扩展，数字波形失真。修正低、高字节的无符号拼接，并用带负值的共享 HEAP8 补回归。最终站点与初次预览的 QEMU WASM 完全一致，唯一音频适配器变化是上述字节拼接。两段旧执行均保留各自的摘要和原始报告 SHA-256。

## 最终执行

最终站点清单 SHA-256 为 a803f0b574e2597e7e7230612fa222c3d2f63391959cd887f6aaf63b1a9d9770。运行时清单 SHA-256 为 e2786abd7b9a10880aa170d68a24f493409a45a20d20fd3a9acf55cc3553cf55，WASM SHA-256 为 ece9223efc171031b178e7b49b35100a5cddbf8958663fc7ab3e11a5840c0f57。站点由常用导出器按显式音频预览模式生成，运行时在给定源码构建的基础上重新编译两个单元，并保留原基线对应的源码归档。该工作台预览未部署，尚须在集成分支上完整重建对应源码包并重跑。

Arduino 通过实际的本地 BIN 文件选择和 Start 执行，挂载哈希匹配的 session-copy microSD。实际连接的浏览器 AudioContext 分析节点读回 48 kHz 波形，最多观测 0.00549 RMS。原固件音量保持不变。录得的非零采样数 575,037 与先前真实描述符捕获一致。

UIFlow2 使用默认官方 v2.5.3 基底，保留标准启动环境和原始 Python 文件。虚拟输入由 16 kHz 有符号 16 位 440 Hz 源经现有 I²S RX/GDMA 到达固件。三个实际屏幕标记为录制、播放和完成。输出峰值所在频率档为 445.3125 Hz，分析窗口为 2,048 采样，频率分辨率为 23.4375 Hz。观察到的最大 RMS 为 0.12374。编辑器中断与原始程序同一会话，并收到原始串口执行回应。

两条路径均由 Chrome 的页面分析节点观察数字信号。真实页面以 48 kHz 连接至 AudioContext 的输出目标。在 Chrome 无头运行中未测量扬声器、耳机或麦克风的物理声学。两个案例分别清理工作台 iframe、上下文和 6 个 Worker，无遗留 Worker。

## 交付边界

- WAV 的原始数字输出约为 −45 dBFS RMS。实际主机响度取决于浏览器和系统音量。
- 麦克风例程使用生成的固定采样，只在已知例程的编辑器运行期间注入虚拟 I²S 输入。
- UIFlow2 Speaker 加载单独的音频素材，本次没有打包。原素材的再分发授权和公开获取路径仍是 #248 的待办。
- 浏览器预览开关及版本限定随导出配置启动。默认部署方式仍采用默认导出选项。完整来源锁、实际部署、跨浏览器兼容、文档嵌入和并发性能需要独立验收。
- 回滚可停用音频预览导出选项。独立撤销 I²S 补丁时，应先撤销 PCM 层，再撤销描述符定时层并重新生成锁定运行时。

[Issue #248](https://github.com/m5agent/m5stack-esp-emulator/issues/248) · [Arduino WAV 文档](https://docs.m5stack.com/en/arduino/m5cores3/wav) · [microSD 示例 Issue #253](https://github.com/m5agent/m5stack-esp-emulator/issues/253) · [原始 UIFlow2 Mic 源码](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/hardware/mic/cores3_mic_example.py) · [可执行复跑步骤](code/replay.md) · [最终浏览器摘要](evidence/browser-audio.summary.json)

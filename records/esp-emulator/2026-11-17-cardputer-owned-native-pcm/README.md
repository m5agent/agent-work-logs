# 初代 Cardputer 普通会话的原生 PCM 取证

- 日期 `2026-11-17`
- 结果 `PASS`（注入端、实际 I2S 输出、ZIP 与静音对照）
- 类型 `code_change`
- 来源 初代 Cardputer 原生音频路径
- 版本 `m5stack-esp-emulator @ 4160e5d27732742052e2246bffb773a718373ca6`
- 环境 隔离原生 Xtensa QEMU、Cardputer K132 与 Cardputer ADV 原厂 UIFlow2

同一镜像及 QEMU 下，修复使初代 Cardputer 的普通会话完成麦克风录制与播放，并保存注入源及实际 I2S DMA PCM。两款设备的音调和静音对照均通过。冻结复验测得麦克风 440.078 Hz，播放输出 660.019 Hz。证据为模拟器的数字采样。

- [复现、对照和清理](report.md)
- [结构化记录](run.json)
- [两款设备音调和静音对照](evidence/board-audio-summary.json)
- [冻结包复验和初次部分结果](evidence/combined-audio-summary.json)

真机、声学和浏览器 WASM 均未运行。未提交 Burner。

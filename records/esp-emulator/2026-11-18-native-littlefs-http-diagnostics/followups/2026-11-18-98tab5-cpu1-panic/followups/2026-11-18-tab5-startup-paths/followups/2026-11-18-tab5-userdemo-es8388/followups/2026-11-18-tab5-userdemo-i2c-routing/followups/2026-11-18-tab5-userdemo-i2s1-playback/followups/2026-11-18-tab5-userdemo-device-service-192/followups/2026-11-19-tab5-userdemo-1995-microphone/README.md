# Tab5 UserDemo V0.4 原版双麦录制和回放

- 日期：2026-11-19
- 结果：PASS（限定原版和已验证的 Tab5 GT911/ILI9881C 原生虚拟设备）
- 工作类型：code_change / virtual-device validation
- 来源：[UserDemo V0.4 双麦页面](https://github.com/m5stack/M5Tab5-UserDemo/blob/V0.4/app/apps/app_launcher/view/panel_dual_mic.cpp)
- 环境：Device Service 1.99.5，macOS arm64，官方 esp-emu 1.1.0

Device Service 从上传的 WAV 为原版提供 I²S1 接收数据。原版显示两路波形并完成
REC、PLAY 和 IDLE 三个阶段。左声道回放以 440 Hz 为主，右声道以 880 Hz 为主。
静音对照的双麦波形平直，动作区间 PCM 全零。复位后保留音源绑定，再次录制回放。
错误的双声道 WAV 和权限不足的请求均在分配租约前拒绝。

- [方法、源与验证边界](report.md)
- [结构化记录](run.json)
- [原版音源、静音、权限和复位对照](evidence/tab5-userdemo-microphone-product.summary.json)
- [最终 WAV 解析器复验](evidence/tab5-userdemo-microphone-final-replay.summary.json)

未运行真机声学、其他固件或浏览器 WASM。Burner 未提交。

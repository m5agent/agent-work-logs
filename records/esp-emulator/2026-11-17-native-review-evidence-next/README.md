# ESP Emulator 原生固件审核后续验证

- 日期 `2026-11-17`
- 结果 `PARTIAL`
- 工作类型 `code_change`
- 问题来源 原生运行时和固件审核能力复测
- 源码版本 `m5stack-esp-emulator @ cccc83b95d4c89f043d6d6d77d21161bc5ece106`
- 环境 隔离 Device Service、原生 Xtensa QEMU、原生 ESP32-C6 QEMU 与 Tab5 ESP32-P4 `esp-emu`

## 结论

五项验证覆盖 Nesso N1 的当前 PC、Tab5 原版应用触摸、NC1020 原版 SD 存档、Dial 音频模块的 UART 控制及 Device Service 能力预检。NC1020 冷导入和界面、Dial 原版界面和音频输出、Tab5 通用审核交互仍有验证缺口。

## 关键证据

- Nesso N1 运行与暂停期间均读取 CPU0。崩溃探针的当前 PC 和同会话固件保留的 MEPC 分别取证，Core2 对照保持双核行为。[C6 与 Core2 摘要](evidence/c6-live-pc-summary.json)
- Tab5 原版 Arduventure 的空白触点保持帧不变，速度、新游戏键、名称确认及四向光标均有应用变化。有序触摸报告和释放另由 ST7123 客体探针确认。[Tab5 摘要](evidence/tab5-st7123-touch-summary.json)
- NC1020 原版在 SPI SD 写出 99,384 字节存档，新会话恢复固定状态。FAT16 冷导入到 96 bank 后触发 CPU1 watchdog，载入后的数字画面仍为黑帧。[NC1020 摘要](evidence/nc1020-save-summary.json)
- Dial PORT A/B 使用原驱动完成七轨索引和控制，空介质对照报告零轨。原版旋钮变化随后发出曲目 4、2 的 UART 播放命令。[Dial 摘要](evidence/dial-audioplayer-summary.json)
- 能力查询区分型号支持、后端缺失与同板型用例登记。ADV 隔离预检后，同服务原版 MP3 会话执行 SPI 读卡和数字 PCM 播放。[能力预检摘要](evidence/device-capabilities-summary.json)

## 文件

- [完整报告](report.md)
- [结构化运行登记](run.json)
- [有界证据](evidence/)
- 补丁和重建工程见源码提交。此记录不附二进制或原始 ZIP。

## 未覆盖项

物理硬件和浏览器 WASM 未运行。设备能力查询只读运行时和目录，固件应用断言来自独立的同会话行为证据。通用审核的人工复核状态按原记录保留，本轮未提交 Burner。

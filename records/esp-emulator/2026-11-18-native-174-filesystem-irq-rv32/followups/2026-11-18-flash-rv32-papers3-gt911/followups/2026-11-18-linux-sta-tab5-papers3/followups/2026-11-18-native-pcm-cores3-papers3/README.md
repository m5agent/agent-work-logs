# Cardputer 原生 PCM、CoreS3 Joystick 审核与 PaperS3 浏览器归因

- 日期 `2026-11-18`
- 整体结果 `PARTIAL`，工作类型 `report`
- 集成源码 `731817add38c34e6d2a58f8dcde646cd7ded3f46`，审核源码 `4315174c8231b7ac5dd27fc41083fbf20c112106`
- 来源为 ESP Emulator 原生 Device Service、保存快照审核和 PaperS3 原版固件浏览器复验
- 环境为隔离原生 QEMU Device Service、CoreS3 Port A 虚拟 U024 和独立 Chromium QEMU WASM

Cardputer 与 Cardputer ADV 的虚拟麦克风都读到替换的 523.217 Hz 音调，原生 I2S DMA 输出都测得 660.657 Hz。CoreS3 两次保存快照审核的总线数据与来宾读值相符。PaperS3 在 ET047 无新增扫描且浏览器没有帧请求时仍漏报触摸，前台驱动服务间隔的原因待定位。实体音响、机械触摸和电子纸光学表现均为 `NOT RUN`。

[报告](report.md) · [结构化结果](run.json) · [脱敏证据索引](evidence/README.md) · [上一次复验](../../report.md)

# UIFlow2 文档素材、麦克风和 Cardputer-Adv CC1101

- 日期 `2026-11-25`
- 结果 `FAIL`（指定例程的板级动作和画面条件），`PARTIAL`（固件版本及实际外设接入）
- 工作类型 `report`
- 来源 [CoreS3 显示](https://uiflow-micropython.readthedocs.io/en/latest/hardware/display.html) · [扬声器](https://uiflow-micropython.readthedocs.io/en/latest/hardware/speaker.html) · [麦克风](https://uiflow-micropython.readthedocs.io/en/latest/hardware/mic.html) · [Cardputer-Adv CC1101 Cap](https://uiflow-micropython.readthedocs.io/en/latest/cap/cc1101.html)
- 源码 [m5stack-esp-emulator @ afd1c635fa702b201508a5d5d689cb67ed1243f3](https://github.com/m5agent/m5stack-esp-emulator/tree/afd1c635fa702b201508a5d5d689cb67ed1243f3) 的编程镜像对照和 CoreS3 调度候选
- 环境 Chrome 158.0.8127.37、macOS、浏览器 WASM 虚拟设备验证

指定 CoreS3 例程走了实际来宾。图形例程的 QR 被裁切，扬声器例程缺失素材，麦克风例程留在初始界面且无法用编辑器中断。Cardputer-Adv 的两个 RF 例程停在 CC1101 初始化，NFC 例程在固定 SDK 的构造函数中抛出错误。

- [复现和验收](report.md)
- [结构化记录](run.json)
- [脱敏源文件、固件、串口、屏幕与停止摘要](evidence/editor-and-cc1101-summary.json)

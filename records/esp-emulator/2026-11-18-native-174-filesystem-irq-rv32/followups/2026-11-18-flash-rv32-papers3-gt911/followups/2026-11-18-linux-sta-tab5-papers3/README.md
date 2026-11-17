# Linux 原生 STA、Tab5 审核归因与 PaperS3 触摸复验

- 日期 `2026-11-18`
- 整体结果 `PARTIAL`，工作类型 `report`
- ESP Emulator 归档源码 `36b091f9766209d2fbc1c28d717ea065cd035d96`，审核源码 `212843e7753195b8878943c97429b00c6d385995`
- 环境为隔离 Linux 原生 Device Service、Tab5 原生 DSI 审核和独立 Chromium QEMU WASM

Cardputer 与 Cardputer ADV 在 Linux 私有网络命名空间完成虚拟 STA 数据面及审核入场。Tab5 同一原版无 ELF 审核保留触摸控制器到达、画面未变与旧服务拒绝滑动的独立证据。PaperS3 的 12 次浏览器接触均满足观测时长下限，四次中点读到 GT911 ready，所测应用图标仍为 0/12。

[报告](report.md) · [结构化结果](run.json) · [脱敏证据索引](evidence/README.md)

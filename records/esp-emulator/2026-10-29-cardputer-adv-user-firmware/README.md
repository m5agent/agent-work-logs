# ESP Emulator Cardputer-ADV 用户固件兼容

- 日期：`2026-10-29`
- 结果：`PASS`（virtual-device）
- 工作类型：`code_change`
- 问题来源：用户提供的 `GAME Piano Tiles ADV 2.0`
- 源码版本：`m5agent/m5stack-esp-emulator@8b4d857bb8a6ebadb32d4a05a1d0ec90fd5adfa8`
- 环境：Chromium 浏览器、QEMU WASM、Cardputer-ADV 虚拟设备

## 结论

同一完整 Flash `470aabe2…872f0a` 已能完整显示、按应用方向自动旋转设备、
消除 ADC calibration 循环错误，并通过旧矩阵兼容路径接收 Enter 进入游戏。
5.0126 秒墙钟对应 5.0119 秒虚拟时间。物理硬件未执行。

## 关键证据

- 原生帧：`240×135`，全部像素边界有内容。
- 平面与 3D：`135×240` 竖屏自动旋转，无黑边裁切。
- 串口：ADC calibration 错误 `0`。
- 输入：Enter 保持 500 ms 后画面切换，帧序号差 `23`。
- 源码补丁：干净应用 49 个 patch 后，147 个 patched-file SHA 全部匹配锁文件。

固件发布于 M5GFX
`5f8a783f7dbc07e8ce5c19cf8779829d1eefcde1` 修复之前，因此仍上报 board
14。兼容输入只在 guest 实际执行旧 push-pull 矩阵扫描时启用。

## 文件

- `report.md`：根因、修复、执行和边界。
- `run.json`：结构化记录。
- `evidence/summary.json`：运行结果、哈希和验证项。

## 未覆盖项

物理 LCD 光学方向、色域、背光、键盘电气特性、真机时序和 ADV 原生旧键盘
接线均为 `NOT RUN`。CoreS3 `div8` 与 Core2 `icount` 不继承本记录的墙钟比例。

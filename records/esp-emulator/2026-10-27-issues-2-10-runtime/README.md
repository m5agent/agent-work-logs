# ESP Emulator GitHub issues #2–#10 顺序复测与 Unit 修复

- 日期：`2026-10-27`
- 结果：`PARTIAL`
- 工作类型：`issue`
- 问题来源：GitHub issues #2–#10
- 源码版本：`m5stack-esp-emulator @ a0ad8150b112afe1273100514c7ef0808bd4477b`
- 实现 head：`0257064fbb7faf9bb5c4238d74b2e588c92c1f4d`
- PR：[#13](https://github.com/m5agent/m5stack-esp-emulator/pull/13)
- 环境：macOS arm64、Python 3.12.14、Node.js、最终 Xtensa QEMU cold build；未使用物理硬件

## 结论

在最新模拟器上依次复测 #2–#10。#2/#3 仍复现 Core2 WDT/reset 和
302-byte 纯黑帧，保持 open；#4 已由既有主线修复解决；#5–#8 的 Servo8
HAT、8Servos、Joystick2 和 NFC Unit 控制器路径通过；#9/#10 的
Cardputer-ADV app-bound synthetic ADC calibration 和启动路径通过。#4–#10
满足关闭条件。

该结论是 `virtual-device validation`。物理硬件、舵机运动/电流、NFC
RF/天线、机械标定、ADC 电气精度和 Tetris 逐帧游戏逻辑均为 `NOT RUN`。

## 关键证据

- runtime `9aca9a8db5143ad133510795cd228ed8ac23c388ea197267d7b2b4750e58eb82`；
- source receipt `1219a45d8ad495509e01088f87af5fe7e41719bb4661e6e60afc42fdce035b26`；
- 14 patch / 109 source；`0048` reverse-check PASS；
- platform `1241` tests PASS / `1 skipped`；
- 四个生成检查、Unit 定向测试、offline Unit fault controls、Node browser
  contracts 和 GitHub CI 两 job PASS；
- 九个 `/api/v1` session 均在 ZIP-before-stop 后以 `purge=0` 停止；
- #4–#8 的固件/源码 SHA、串口 marker、QOM/data-plane 值、frame 和
  evidence ZIP SHA 见 [结构化摘要](evidence/summary.json)；
- #9/#10 evidence 包含 `units/adc-calibration.json`，且不修改 identity/security eFuse。

## 文件

- [report.md](report.md)：逐 issue 结论、执行路径、证据和边界
- [run.json](run.json)：机器可读记录
- `evidence/summary.json`：脱敏后的 runtime、issue、frame 和数据面摘要
- `evidence/frames/`：九个 session 的最终 PNG
- `code/`：#4–#8 的精确最小 guest 测试程序
- `patches/`：本次不复制源码补丁；以合并 commit、PR 和项目内 `0048` 为权威入口

## 未覆盖项

- #2/#3 未解决；只证明当前代表 repro 仍失败，不据此关闭。
- 未执行 20–30 分钟完整 UIFlow2 外设矩阵。
- 未使用物理硬件，也未验证模拟器不覆盖的电气、RF、机械和光学属性。
- #10 原始完整 Tetris 源码不可取得；验证覆盖 issue 中列出的完整 setup
  路径和首个成功 frame，不声明 Tetris 游戏逻辑逐帧通过。

# Cardputer-ADV 用户固件兼容报告

## 背景

用户提供的 `GAME Piano Tiles ADV 2.0 (13.06.2026)` 在浏览器 QEMU 中出现
黑边、裁切、疑似时间过快、按键无响应和 ADC calibration 日志刷屏。

完整 Flash SHA256：
`470aabe22c27a764ac0226058a94e856fcb14d767abfb66c41582fa2ac872f0a`。

## 结论

- ADC calibration 错误：修复，运行中计数 `0`。
- 显示：保留 240×320 控制器内存和 M5GFX `(52,40)` 偏移，恢复完整原生帧；
  浏览器识别 135×240 竖屏窗口并同步旋转 3D 设备与平面帧。
- 时钟：5.0126 秒墙钟 / 5.0119 秒虚拟时间，比例 `0.999856`。
- 输入：旧 Cardputer 矩阵兼容路径只在 guest 将 G8/G9/G11 配置为 push-pull
  输出并执行旧扫描后激活；Enter 切换画面。
- 板型：固件早于 M5GFX `5f8a783f`，仍上报 board 14；这是上游固件问题，
  不是把兼容路径宣称为 ADV 原生旧键盘接线。

## 改动范围

- `0019-cardputer-adv-rotated-panel.patch`
- `0020-cardputer-legacy-matrix-and-orientation.patch`
- `0021-board-bias-over-internal-pull.patch`
- 浏览器设备/平面帧同步旋转和面板方向 QOM 查询
- S3 ADC synthetic calibration eFuse

## 执行

最终导出站使用 49-patch QEMU WASM，实际 Chrome 页面启动相同完整 Flash。
页面执行 `Enter` 前后均保留 `135×240` 正向平面帧；串口全程无
`Guru Meditation`、interrupt-WDT 或 ADC calibration 错误。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `PASS` | 干净 patch 序列应用，147 个 patched-file SHA 与 lock 全部一致 |
| transport | `PASS` | 串口、SPI 面板窗口、TCA/旧矩阵输入路径均在同 guest 运行 |
| device_response | `PASS` | ADC 错误为 0，Enter 触发游戏画面切换 |
| data_behavior | `PASS` | 原生帧序号差 23，平面帧 SHA 变化 |
| visual_or_physical | `PASS`（virtual） / `NOT RUN`（physical） | 完整 240×135 原生帧、135×240 正向平面帧和 3D 同步旋转 |

## 验证边界

没有验证物理 LCD 光学方向、色域、背光、键盘触点、电气特性或真机时序。
旧矩阵兼容不是物理 ADV 接线模型。其它 S3 板型只共享 ADC eFuse 基线，仍需各自
固件和显示/输入验证。

## 风险与回滚

兼容路径由 guest 的实际旧扫描模式门控，不改变 TCA8418 主路径。回滚时可移除
`0020`；面板显示回滚到 `0019` 之前的 320×240 裁切会产生已知的竖屏黑边问题。

## 链接

- 源码 PR：<https://github.com/m5agent/m5stack-esp-emulator/pull/39>
- 公开预览：<https://m5agent.github.io/m5stack-esp-emulator/>
- 仓内证据：
  <https://github.com/m5agent/m5stack-esp-emulator/blob/8b4d857bb8a6ebadb32d4a05a1d0ec90fd5adfa8/docs/evidence/2026-10-29-cardputer-adv-user-firmware/README.md>

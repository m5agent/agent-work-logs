# 新 WASM 的 ADV 板号探测和 CoreS3 来宾复位边界

- 日期 `2026-11-25`
- 结果 `PASS`（ADV 原 Arduino Display、Keyboard 及三个回归设备用例），`FAIL`（CoreS3 来宾热复位），`PASS`（CoreS3 v2.5.5 隔离预览指定的图形和按钮）
- 工作类型 `code_change`
- 来源 [ADV #245](https://github.com/m5agent/m5stack-esp-emulator/issues/245) · [版本问题 #249](https://github.com/m5agent/m5stack-esp-emulator/issues/249)
- 源码 `afd1c635…1243f3`，板号候选 `a4acad97…5a`
- 环境 Chrome 158.0.8127.37、macOS，浏览器 WASM 虚拟设备验证

从源重建 WASM 的 ADV 板号补丁恢复了原 Arduino 显示与键盘。官方 UIFlow2 键盘、K132 原厂启动和 CoreS3 触摸对照通过。CoreS3 工作台的宿主 QMP Reset 会恢复，来宾主动发起的热复位未恢复。v2.5.5 隔离预览证实原图形二维码解码及单例 M5UI 按钮释放。

- [结论和已验证边界](report.md)
- [机器可读记录](run.json)
- [ADV 板号源层、失败对照和设备回归](evidence/cardputer-adv-board-probe-summary.json)
- [CoreS3 三种实际复位](evidence/cores3-guest-reset-summary.json)
- [CoreS3 UIFlow2 v2.5.5 正常时钟预览](evidence/cores3-uiflow-v255-preview-summary.json)

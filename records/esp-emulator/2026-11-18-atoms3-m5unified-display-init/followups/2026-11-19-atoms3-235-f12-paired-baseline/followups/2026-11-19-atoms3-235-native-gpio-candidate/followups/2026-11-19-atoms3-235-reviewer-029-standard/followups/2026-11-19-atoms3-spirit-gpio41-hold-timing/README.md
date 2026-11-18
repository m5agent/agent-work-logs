# AtomS3 Spirit Level 原版 GPIO41 按压复验

- 日期 2026-11-19
- 结果 `PARTIAL`。GPIO41 送达、模式切换和归零效果已验证。标准时长的应用行为仍待复验。
- 工作类型 同版原生虚拟设备验证。
- 问题来源 [AtomS3 #235 后续](https://github.com/m5agent/m5stack-esp-emulator/issues/235)与[前序标准审核](../../README.md)。
- 源码版本 Device Service 1.99.2 `c25fdfc9` 与 1.99.3 候选 `cd129680`；同一个签名 Xtensa QEMU。
- 环境 两个独立的 macOS 原生 AtomS3 会话，均使用 `m5atoms3-st7735` 和同一份 Spirit Level v1.0.0 完整原版。

## 结果

用 GPIO41 对照确认，短按依次切换 BUBBLE、TUBE、ANGLE。宿主配对请求 0.600 秒时，GPIO41 实测相隔 611.131 毫秒，原版在固定倾斜下显示 `ZERO SET`。候选的单次按键 API 请求中，600 和 610 毫秒保留原倾角，700 毫秒归零，2200 毫秒显示归零，2350 毫秒显示重置并恢复原倾角。

每次都核对真实模拟 GPIO 边沿。两轮证据 ZIP 均通过 CRC、8 项成员哈希、原版应用区域和同会话核验。停止后会话历史保留、Flash 已释放、活动租约为零。观察结果保留实际时点，通用阈值、实机、断电重启和候选的标准 Reviewer 路径未验证。Burner 未提交。

[复验报告](report.md) · [运行记录](run.json) · [脱敏证据摘要](evidence/atoms3-spirit-gpio41-timing.summary.json)

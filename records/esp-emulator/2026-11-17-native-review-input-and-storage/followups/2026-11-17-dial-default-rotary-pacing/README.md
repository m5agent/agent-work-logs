# Dial 原生普通输入与 UIFlow2 RotaryIRQ 复验

- 日期 `2026-11-17`
- 结果 `PARTIAL`，普通输入通过，显式高速应用计数仍有缺口
- 类型 `code_change`
- 候选源码 `693c56948c2458cf8e24c800832f7600438f4b45`
- 环境 隔离 Device Service、原生 Xtensa QEMU、同一 Dial UIFlow2 组合镜像

支持 paced-detents 的普通输入在省略间隔时采用 35 ms。来宾默认动作 12/12 计数准确，最终源码同路径的四个正负动作再次通过。显式 5 ms 仍交付完整模型边沿，带同步重画的原驱动会少计。旧运行时保留 5 ms 的回执和动作。

- [报告与复现](report.md)
- [结构化记录](run.json)
- [默认、快速和旧运行时证据](evidence/dial-default-pace-summary.json)
- [精确集成源码复验](evidence/integrated-dial-confirmation-summary.json)

[最终验证源码与复现](https://github.com/m5agent/m5stack-esp-emulator/blob/37fc8963d77bf806cde4fa16ea11e31b5a98b4d7/docs/evidence/2026-11-17-semantic-native-input/README.md)

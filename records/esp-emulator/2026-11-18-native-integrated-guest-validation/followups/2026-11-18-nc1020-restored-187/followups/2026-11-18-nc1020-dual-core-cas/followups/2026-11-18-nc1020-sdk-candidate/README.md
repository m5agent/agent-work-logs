# NC1020 原版与 SPI 锁 SDK 回移候选对照

- 日期为 `2026-11-18`，时区为 Asia/Shanghai。
- 结果为 `PARTIAL`，工作类型为 `report`。
- 环境为 同一冻结 K132 原生运行时和独立重建候选。
- 源码版本为 `d25eae8db848918e9cafebc127a53a0f989941d4`。
- 来源为 [固定问题或前次报告](https://github.com/m5agent/agent-work-logs/blob/5a6d032a13e35523cd59034c27372d09c5131287/records/esp-emulator/2026-11-18-native-integrated-guest-validation/followups/2026-11-18-nc1020-restored-187/followups/2026-11-18-nc1020-dual-core-cas/README.md)。

## 结论

同一冻结运行时与存档素材下，原版 1/3 完整显示，独立 SDK 回移候选 4/4 完整显示。七轮均恢复同一存档，发布者的原版保持不变。

## 证据

- [执行报告](report.md)记录运行身份、对照与各层限制。
- [运行清单](run.json)记录可校验输入与状态。
- [有界证据](evidence/README.md)保留映像、帧、串口和 ZIP 哈希。
- 补丁与可重建工程由报告中的固定源码引用提供。

## 验证范围

结果覆盖该候选在这一份已保存状态上的原生虚拟设备复验。完整原版稳定性、实机、浏览器和 Burner 未验证。

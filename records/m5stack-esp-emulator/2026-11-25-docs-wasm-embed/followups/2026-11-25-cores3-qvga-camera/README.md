# CoreS3 Camera QVGA 浏览器短帧修复

- 日期 2026-11-25
- 工作类型 fix，virtual-device validation
- 设备 CoreS3，Chrome 158.0.8127.37
- 问题来源 [模拟器 #243](https://github.com/m5agent/m5stack-esp-emulator/issues/243)
- 源码基线 `f49479080790213c76e796108b6ac5bed6adce7c`，候选 `7576e35098c0226773263fc8e375d389f1860104`
- 物理摄像头、原生运行时及正式托管未执行

旧版本可间歇显示完整图像，同时丢弃 15,360 字节短帧。按实际控制器路径修复后，标准工作台运行官方例程持续显示预期的 320×240 固定场景。30 秒采样的 118 帧均匹配目标图案，未出现短帧或溢出；停止后 Worker 全部关闭。独立带跟踪对照有 958/959 次完整采集，一次提前停止随后自动恢复。

- [根因、对照和复现步骤](report.md)
- [结构化执行记录](run.json)
- [原始失败与 DMA 分组对照](evidence/controller-comparison.summary.json)
- [完整锁定源构建](evidence/locked-build.summary.json)
- [标准工作台原例程验收](evidence/standard-workbench.summary.json)

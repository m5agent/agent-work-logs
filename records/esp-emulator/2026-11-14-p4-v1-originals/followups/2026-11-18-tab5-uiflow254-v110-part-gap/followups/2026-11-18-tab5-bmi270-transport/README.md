# Tab5 原版 UIFlow2 BMI270 大请求与面板分支

- 日期为 `2026-11-18`，时区为 Asia/Shanghai。
- 结果为 `PARTIAL`，工作类型为 `issue`。
- 环境为 冻结原生 QEMU 和三条隔离 Part 诊断。
- 源码版本为 `174c6d42048bf12f315e8b572948f17638d0bb77`。
- 来源为 [固定问题或前次报告](https://github.com/m5agent/m5stack-esp-emulator/issues/188)。

## 结论

三轮均解码到原版 BMI270 的 8,192 字节配置事务。ST7123 在隔离诊断 Part 下显示离线启动页。GT911 的 DSI 零值读回仍存在。

## 证据

- [执行报告](report.md)记录运行身份、对照与各层限制。
- [运行清单](run.json)记录可校验输入与状态。
- [有界证据](evidence/README.md)保留映像、帧、串口和 ZIP 哈希。
- 补丁与可重建工程由报告中的固定源码引用提供。

## 验证范围

本轮覆盖原版配置传输和 ST7123 的离线启动页。触摸、配对、浏览器、实体设备和生产候选验收均为 NOT RUN。Burner 未提交。

## 后续复验

[正式 Part 和最终源码复验](followups/2026-11-18-tab5-bmi270-native-part/README.md)记录原版 BMI270 初始化、ST7123 点击和 GT911 剩余面板缺口。

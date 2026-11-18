# Tab5 原版 UIFlow2 V2.5.4 在 esp-emu 1.1.0 的双 Part 对照

- 日期为 `2026-11-18`，时区为 Asia/Shanghai
- 结果为 `PARTIAL`
- 工作类型为 `issue`
- 问题来源为 [公开 issue #188](https://github.com/m5agent/m5stack-esp-emulator/issues/188)
- 源码版本为 `0e376abc91ddf8252eb565cb1b54204be8e1f089`
- 环境为 隔离 Device Service 1.89.0 和两套原生 Tab5 DSI Part

## 结论

两套 Part 都在同一个超长编码请求处退出，原版应用可用性保持开放。

## 关键证据

- 两个原版会话和同一规范化镜像的哈希均保留。
- 主机编码请求 8,205 字节，Part 缓冲上限 1,024 字节。
- 两轮均留存证据 ZIP，进程、Flash 和租约均清理。

## 文件

- [完整报告](report.md)记录执行步骤、观察与限制。
- [运行清单](run.json)记录输入身份与各层判据。
- [有界证据](evidence/README.md)记录脱敏范围和原始产物哈希。
- 补丁和测试工程不适用。本条记录沿既有执行路径进行复验。

## 未覆盖项

客体 I²C 线级长度和异常来源待定位。浏览器、触摸及实体设备尚未执行，Burner 未提交。

## 后续复验

[Tab5 原版 UIFlow2 BMI270 大请求与面板分支](followups/2026-11-18-tab5-bmi270-transport/README.md)

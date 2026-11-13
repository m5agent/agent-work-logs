# ESP Emulator：#211 浏览器固件验收收口

- 日期：`2026-11-13`（Asia/Shanghai）。
- 结果：`PASS`，限定两份固定固件和当前隔离导出。
- 工作类型：`issue` / `code_change`。
- 问题来源：[#211 浏览器上传、首帧、双 SHA、输入与 REPL 边界](https://github.com/m5agent/m5stack-esp-emulator/issues/211)。
- 源码版本：[m5stack-esp-emulator @ 34d495245204af82f6c3df847d43ea9eebc6d884](https://github.com/m5agent/m5stack-esp-emulator/tree/34d495245204af82f6c3df847d43ea9eebc6d884)。
- 环境：Chrome 实际 browser-WASM virtual-device validation；无 Device Service/native guest。

原有页面与 Skill 改动完成验收：demo 的49项检查及原报告同一原版 BIN 的13项检查通过。
真实触摸/PIR、串口与像素、原始/运行双 SHA、REPL 独立不可用状态、下载 JSON、错误
SHA 负控及实际 CDP Worker 清场分别验证。修复本地验收服务器的缺失文件重复响应头
错误，首次基础设施失败独立保留，不作为固件失败。

- [report.md](report.md)：结果、复现、修复和边界。
- [run.json](run.json)：结构化身份与检查。
- [summary.json](evidence/summary.json)：脱敏行为与哈希证据。
- `patches/`、`code/`：不适用；公开固定源码与检查入口在报告中引用。

此记录不代表新 Pages 发布、浏览器公网/配对、任意 stock REPL 或物理硬件。
扩展的 file URL 权限阻断未复现；其 native-picker 回退已明确写入 Skill。

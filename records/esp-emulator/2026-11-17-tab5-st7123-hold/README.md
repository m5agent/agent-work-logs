# Tab5 ST7123 长按与原版审核

- 日期 `2026-11-17`
- 结果 `PARTIAL`，原生单点长按和已声明点按通过，整机关机待验证
- 工作类型 `code_change`
- 来源 Tab5 无 ELF 的原生固件交互审核
- 源码 `m5stack-esp-emulator @ dc6853453a64f315a09b691c3631d9c2d4b3c08e`
- 环境 隔离 Device Service、原生 ESP32-P4 和编译固定的 ST7123 Part

原生探针测得 1,201,970 微秒的连续接触和一次释放。原版 Arduventure 的九个点按经原生帧门槛确认，中心长按由同一客体读回。长按原版电源图标触发关机画面和板级 I²C 脉冲，关机终态保留 `PARTIAL`。原版 CarPlay 的 GT911 控制路径通过回归。

- [报告与复现入口](report.md)
- [结构化记录](run.json)
- [原生控制器和原版复验摘要](evidence/native-hold-summary.json)
- [冻结版本的同会话审核摘要](evidence/snapshot-review-summary.json)

真机、浏览器 WASM 和多点触摸未验收。本轮未触发 Burner 提交，原始固件、截图和 ZIP 未包含在记录中。

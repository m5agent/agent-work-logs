# Tab5 CarPlay 原版 DSI 首帧复验

- 日期 `2026-11-17`
- 结果 `PARTIAL`
- 工作类型 `code_change`
- 问题来源 CarPlay 原版审核中的 Tab5 截图缺口
- 源码版本 Device Service `42e282f25c8ad8f0694f97c8a44bd82dd5d0a43c`、审核服务 `55ffc80e7c9ec5e5280a267e875b4c042b54fde3`
- 环境 隔离 Tab5 esp-emu 1.1.0，使用 `gt911-ili9881c` 板型配置。验收层级为 virtual-device validation。

## 结论

同一原版 BIN 无匹配 ELF 也能取得原生 DSI 首帧。审核在 60.255 秒运行观察中保留了画面和串口，画面显示 CarPlay v1.0.0 等待连接 iPhone。触摸和拖动请求均被拒绝，整体仍需人工复核。

## 关键证据

- 原版 SHA-256 `4f3bb118a5570a6ba885a234fce55b66e28ef26091cfe4f3f2e4c33711471ea3`。
- `720×1280` 真实画面有 921,600 个非黑像素，应用画面就绪检查通过。
- 核验截图、结构化诊断与取证 ZIP 的原始哈希。

## 文件

- [报告](report.md)
- [结构化记录](run.json)
- [脱敏证据](evidence/carplay-native-dsi-summary.json)
- [上一级诊断记录](../../README.md)

原始截图、ZIP 和固件保留在隔离执行证据中。本记录不携带补丁或重建工程。

## 未覆盖项

USB host、连接手机和触摸行为均为 `NOT RUN`。实机、浏览器和生产切换未执行，未提交 Burner。

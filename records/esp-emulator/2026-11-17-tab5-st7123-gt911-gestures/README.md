# Tab5 原版 Arduventure 与 GT911 拖动复验

- 日期 `2026-11-17`
- 结果 `PARTIAL`
- 工作类型 `code_change`
- 问题来源 [Tab5 板型问题 #227](https://github.com/m5agent/m5stack-esp-emulator/issues/227)
- 源码 `m5agent/m5stack-esp-emulator @ 4fc493abdb305afb795a91f8d2639e71cca5c25f`
- 环境 macOS arm64 上的隔离 Device Service 和 [esp-emu 1.1.0](https://github.com/espressif/esp-emulator/releases/tag/v1.1.0)

## 结论

同一个 Device Service worker 对两份原版按执行 Flash SHA 选择板型，两份原版均正常进入应用画面。

## 关键证据


- Arduventure 1.0.0 通过原生模拟 GPIO 软件 I²C 找到 ST7123，按原始 720×1280 输出游戏启动画面。ST7123 触控仍待验证。
- GT911 探针经原生模拟 IRQ 和 I²C 完成六个位置和释放。在同一个配置的 worker 中，原版 CarPlay 空白拖动保持画面，随后单击打开配对清除确认框。

独立审核 dry-run 中，Arduventure 和 CarPlay 均通过截图与 60 秒观察，两条仍为人工复核，原因分别为 `E_INTERACTION_INPUT_UNSUPPORTED` 和 `E_INTERACTION_CLAIM_PARTIAL`。[隔离复审摘要](evidence/review-dry-run-summary.json)

## 文件

[报告与复现](report.md) · [结构化记录](run.json) · [证据摘要](evidence/tab5-native-summary.json)

只归档派生摘要与取证哈希。原版固件、游戏图像、原始日志及会话 ZIP 不随记录分发。

## 未覆盖项

ST7123 动态触控、Arduventure 游戏操作、USB/iPhone、浏览器触控及物理板卡未执行对应路径。

[最终验证源码与复现](https://github.com/m5agent/m5stack-esp-emulator/blob/37fc8963d77bf806cde4fa16ea11e31b5a98b4d7/tests/firmware/tab5_gt911/README.md)

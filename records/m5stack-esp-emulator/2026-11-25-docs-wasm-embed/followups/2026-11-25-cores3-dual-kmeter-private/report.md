# DualKmeter 原 Blockly 工程与 CoreS3 WASM

官方编辑器从原 `.m5f2` 两次生成完全相同的 774 字节完整 Python，SHA-256 `6765c65ac5e3a6219d762fe2cbc4639301714719646a79b115cc794e2b44fb37`。默认锁定 0046 和私有候选均在 CoreS3 UIFlow2 v2.5.3 工作台以原编辑器运行相同代码，保持组合固件 `b9fe8334…2d49`。默认运行先观察到 `module/dual_kmeter.py` 的 `is_ready()` 抛出 `OSError: 259`，温度未更新。该负对照独立留证。[原工程、生成过程和默认来宾](https://github.com/m5agent/agent-work-logs/tree/580797bfabda169ac3c8885da753059a4ef3a2fb/records/m5stack-esp-emulator/2026-11-25-docs-wasm-embed/followups/2026-11-25-cores3-blockly-source-preview)

私有候选从精确锁定 0049 重新编译两处相关对象，712 个其他链接输入逐字节相同。CoreS3 例程显式启动测试夹具，经原 ESP32-S3 I²C1 和 M-Bus 访问地址 `0x11`。模型的只读 `0x30` 就绪寄存器为零，`0x00` 到 `0x03` 是按读取事务保持一致的 LE32 有符号百分之一摄氏度。固定且有界的输入操作只修改同一来宾 QOM 模型的温度寄存器数据，原始程序通过原驱动读取，浏览器用 OCR 从实际 RGB565 画面验证数字。

| QOM 输入 | 原画面 OCR | I²C 事务 / 读字节 / 写字节 |
| --- | --- | --- |
| 23.50 °C | `23.5` | 204 / 255 / 102 |
| −12.34 °C | `-12.34` | 450 / 561 / 225 |
| 87.65 °C | `87.65` | 688 / 860 / 344 |

三次是同一来宾、同一控制台代次和独立新画面。实际编辑器 Interrupt 返回确认。页面 Stop 正常退出 QEMU，移除 iframe 并回收全部六个 Worker。默认负对照也正常回收。未模拟真实热电偶温度、校准误差、其他通道或物理响应。候选导出为 `publication_eligible=false`，源包只描述 0049 基线。标准工作台明确选择该示例的正式路径需以全量锁定构建重新验证。[官方 M127 模块](https://docs.m5stack.com/en/module/Module13.2_Dual_Kmeter) · [固件、构建、数据面和清理摘要](evidence/dualkmeter-candidate.summary.json)

## 复现

1. 按 [0049 原运行物](https://github.com/m5agent/agent-work-logs/tree/6a40219a3ef6aace200e4066db38546634ae59e0/records/m5stack-esp-emulator/2026-11-25-docs-wasm-embed/followups/2026-11-25-cardputer-adv-signed-portrait-locked-0049) 取得相同的源码锁、完整构建缓存和本地 `/showcase/` 导出。校验实际 SHA-256。
2. 在独立实验目录用 [C 补丁](patches/private-cores3-dual-kmeter.patch) 和 [重链接脚本](code/relink-private-0049.py) 从同一基线制作候选。准备脚本根据复现环境的本地目录选取准确输入。用 [封存脚本](code/stage-private-0049.py) 验证并封存私有静态站点。
3. 在官方编辑器生成原工程完整 Python。其文件名为 `dualkmeter.official.full-preview.py`，执行前必须和记录中的 SHA-256 一致。编译 [OCR 辅助程序](code/read-display-text.swift)。放置 [浏览器脚本](code/run-private-dual-kmeter.mjs) 于自有实验目录，设置 `M5_DUAL_KMETER_RUN=1`、`M5_PUBLIC_SITE`、`M5_DUAL_KMETER_SITE` 和 `M5_DUAL_KMETER_WASM`。运行 `node run-private-dual-kmeter.mjs dualkmeter browser-dual-kmeter-candidate-1`。只用新输出目录，保留真实浏览器报告和清理观测。

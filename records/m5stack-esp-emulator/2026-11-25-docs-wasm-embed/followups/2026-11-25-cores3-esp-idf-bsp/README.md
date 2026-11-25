# CoreS3 ESP-IDF BSP 原 LVGL 示例

- 日期 `2026-11-25`
- 结果 `FAIL`（当前浏览器 WASM 下的 LVGL 显示），`PASS`（Music 大应用分区构建）
- 工作类型 `report`
- 来源 [CoreS3 ESP-IDF BSP 使用教程](https://docs.m5stack.com/en/esp_idf/m5cores3/bsp)
- 版本 ESP-IDF v5.4.1，espressif/m5stack_core_s3 3.0.2，LVGL 9.6.0~1
- 环境 Chrome 158.0.8127.37、macOS，浏览器 WASM 虚拟设备验证

Widgets、Stress、Benchmark 和 Music 都执行到了原程序的 LVGL 串口日志，但实际 RGB565 只报告黑屏。Widgets 的正常时钟对照仍黑。Music 源码超出默认 1 MB 应用分区，按 SDK 菜单切换到 1.5 MB 大应用分区解决构建阻塞，并在浏览器来宾复验进入应用。

- [可重复构建和观察](report.md)
- [结构化记录](run.json)
- [固件、运行时、串口与像素摘要](evidence/esp-idf-bsp-wasm-summary.json)

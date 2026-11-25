# CoreS3 LVGL Music 横屏配置

- 日期 2026-11-25
- 工作类型 fix，virtual-device validation
- 结果 PASS，横屏布局和播放器触摸反馈
- 设备 CoreS3，Chrome 158.0.8127.37，Apple Silicon macOS
- 文档版本 c83ac05d7115e84e5af683eed3970f32c9015150
- 真机和音频输出 NOT RUN

一个编译选项切换后，在同一锁定 WASM 和 320×240 画面上，曲名、艺人和播放控件并排显示。点按播放和暂停得到实际图标与曲目时间变化。配置说明已在三语正式文档读回。[英文](https://docs.m5stack.com/en/esp_idf/m5cores3/bsp) · [中文](https://docs.m5stack.com/zh_CN/esp_idf/m5cores3/bsp) · [日文](https://docs.m5stack.com/ja/esp_idf/m5cores3/bsp)

- [构建和前后对照](report.md)
- [结构化结果](run.json)
- [对照帧、输入及清理摘要](evidence/music-layout.summary.json)

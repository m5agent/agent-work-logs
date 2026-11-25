# 复现和文档修正

原 ESP-IDF CoreS3 Music 例程使用 LVGL 9.6.0~1 的默认纵向布局。在 320×240 锁定 WASM 画面中进入播放器后，标题顶部裁切，播放控件靠近下边缘。

在独立项目打开 CONFIG_LV_DEMO_MUSIC_LANDSCAPE。其余有效 sdkconfig、Music 应用源码、依赖及大 factory 分区相同。16 MiB 合并镜像 SHA-256 由 4234dda971731a8cf70ab440e8f7c7ff2cd4d6df742c2f13cc6a108b6c833a0d 变为 d721745fa2ab79045dc66ad45d454dd3cd24cd96e84f780c61441ff2350e466b。选项入口为 idf.py menuconfig 中的 Landscape layout。[LVGL Kconfig](https://github.com/lvgl/lvgl/blob/v9.6.0/demos/music/Kconfig#L10-L12)

两组固件使用同一 11c5dea1…0555 WASM、默认 cores3-wasm-vm-div8 及相同显示尺寸。横屏显示完整曲名 Waiting for true love、艺人和五个播放控件。实际触摸坐标 (77,136) 两次按下释放在同一来宾切换播放→暂停→播放图标，时间从 0:00 变为 0:01。原有性能浮层仍可覆盖列表入口的右端，频谱动画触及右边缘。两组都正常退出，CDP 观测到实际 Worker 全部关闭。音频输出为 NOT RUN。

在三语的 BSP Music 小节增加横屏选项。正式站点在 2026-11-25 三页均返回 HTTP 200 并包含 CONFIG_LV_DEMO_MUSIC_LANDSCAPE。回退为删除该建议或恢复原 Kconfig 值。

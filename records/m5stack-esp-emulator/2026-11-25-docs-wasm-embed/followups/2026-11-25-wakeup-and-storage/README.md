# CoreS3 定时唤醒、RTC 和两款设备存储检查

- 日期 `2026-11-25`
- 结果 `FAIL`（CoreS3 定时唤醒，默认浏览器卡槽条件），`PASS`（隔离附件的 PNG、ADV 文件操作），`PARTIAL`（RTC/SNTP 和音频）
- 工作类型 `report`
- 来源 [CoreS3 Wakeup](https://docs.m5stack.com/en/arduino/m5cores3/wakeup) · [CoreS3 SDcard](https://docs.m5stack.com/en/arduino/m5cores3/sdcard) · [ADV SDcard](https://docs.m5stack.com/en/arduino/m5cardputer/sdcard)
- 源码 [m5stack-esp-emulator @ afd1c635fa702b201508a5d5d689cb67ed1243f3](https://github.com/m5agent/m5stack-esp-emulator/tree/afd1c635fa702b201508a5d5d689cb67ed1243f3)
- 环境 Chrome 158.0.8127.37、macOS、浏览器 WASM 虚拟设备验证

CoreS3 唤醒程序的实际触摸进入 PMIC 关机，观察窗未发现 RTC 唤醒。两款设备的浏览器存储原例程在固定 FAT32 附件下完成了指定图片渲染或文件操作。默认页面需要媒体接入。

- [复现和范围](report.md)
- [结构化记录](run.json)
- [帧、固件和控制器摘要](evidence/wakeup-and-storage-summary.json)

# 复现与验证摘要

## 对象

| 项 | 值 |
| --- | --- |
| 设备 | AtomS3（C123，ESP32-S3FN8/8 MiB，ST7735S 128×128） |
| machine | `m5atoms3-st7735` |
| 固件 | AtomS3 Spirit Level v1.0.0，`M5-AtomS3-Spirit-Level-v1.0.0-full.bin`，609,856 B |
| 源 BIN SHA-256 | `c41ba69a80bd83d387808f2c8e562eddbe114733b1bb6ed71aec0c0608e9e393` |
| 会话 flash SHA-256 | `63e9767ca379aaf06483fa0a4bd366e813b5de9c8a832f334cf7217bd97817f6` |
| 审查任务 | `job-bfe1b7e32389`（`SIM_PARTIAL` / `E_NO_FRAME`） |

## 离线复跑

```sh
M5SW_SPI_XFER_TRACE=1 M5SW_SPI_TRACE=1 M5SW_PANEL_DC_TRACE=1 \
qemu-system-xtensa -M m5atoms3-st7735 -m 0 -L <pc-bios> \
  -drive file=<merged-8MiB>.bin,if=mtd,format=raw \
  -drive if=none,id=efuse,file=<efuse>.bin,format=raw \
  -global driver=nvram.esp32s3.efuse,property=drive,value=efuse \
  -serial file:serial.log -display none
```

GC9107 变体：追加 `M5SW_ATOMS3_GC9107=1`，结果相同。

## 观察

- 串口 314 B，尾行为 `[   449][E][Preferences.cpp:503] getBytesLength(): nvs_get_blob len fail: off NOT_FOUND`。
- `M5SW_I2C_TRACE`：MPU6886 初始化 1 次，随后 2,759 轮 `0x3A–0x48` 突发读。
- SPI / 面板 trace：0 条传输、0 条命令。
- 帧：128×128，16,384 像素全 0，unique colors 1，SHA-256 `7659100791b0b0d9d5707576f6d04cdae4e769ae4ba3034169540fe3990efae5`。
- 崩溃诊断 `no_evidence`；QMP PC 位于 FreeRTOS idle `waiti` 桩；flash `changed_bytes=0`；QOM diff 为空。

## 结论边界

virtual-device validation；未做物理 AtomS3、USB CDC 串口捕获、输入注入与探测返回值插桩（`NOT RUN`）。完整归因文本见 [issue #235](https://github.com/m5agent/m5stack-esp-emulator/issues/235)。

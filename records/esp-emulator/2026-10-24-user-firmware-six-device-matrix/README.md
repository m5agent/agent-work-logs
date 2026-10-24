# 六机型用户固件批量仿真回归

- 日期：`2026-10-24`
- 结果：`PARTIAL`
- 工作类型：`virtual-device-regression`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`d0e7abe63bfbaacfc66641a1af0e376252a77f8c`
- 环境：macOS Apple Silicon；本地 Device Service `/api/v1`；QEMU ESP32-S3/S3R8/C6

## 结论

从 M5Burner 热门列表为 StickS3、CoreS3、Cardputer ADV、StopWatch、
Nesso N1、NanoC6 各选取 3 个非基线固件，共 18 个样本，全部经 Device
Service 上传、组合、启动、输入探测、截图/串口取证并正常停止。

最终严格判定为 `11 PASS / 6 PARTIAL / 1 FAIL`。`PASS` 要求应用画面非空、
进程保持运行、无致命串口签名，且至少一个输入探针改变画面或串口输出。

## 关键结果

- StickS3：`3/3 PASS`
- CoreS3：`2/3 PASS`，M5Launcher 在本次 30 秒窗口内为黑屏
- Cardputer ADV：`2/3 PASS`，WiFi CSI Radar 未观察到输入响应
- StopWatch：`3/3 PASS`
- Nesso N1：`1/3 PASS`，Meshtastic 在打印画面后重启，Bruce 无应用画面
- NanoC6：`0/3 PASS`；该机型无屏，Factory Test 与 Evil-NanoC6 为设计内
  `PARTIAL`，Zigbee 固件因 task watchdog 判 `FAIL`
- 测试同时覆盖 6 个并发会话；所有运行在结束时均为 stopped，历史保留
- 物理硬件：`NOT RUN`

## 文件

- `report.md`：选取、执行、逐样本结果、根因分类和剩余边界
- `run.json`：机器可读汇总
- `evidence/verification.summary.json`：脱敏后的 18 样本证据

## 未覆盖项

- Nesso N1 的 stock `hardware.RGB()` 和完整无线外设；
- NanoC6 IEEE 802.15.4/Zigbee 数据面，当前 QEMU 未建模；
- 真实 RF、USB、功耗、声学、光学和机械行为；
- 真机同固件、同输入路径验证。

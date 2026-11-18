# 98TAB5 原版识别合成 NHD 启动盘

2026-11-18 · Tab5 · virtual-device validation

| 路径 | 结果 |
| --- | --- |
| 合成磁盘识别 | **PASS（诊断时序）**。原版 98TAB5 v1.3.0 实际挂载 FAT16，并将根目录 `/HDD.NHD` 打开为 IDE 磁盘。 |
| 普通冷启动 | **FAIL**。合成 NHD 与未上传 SD 镜像两组各观察到 16 次软件复位，均无完整帧。 |
| PC-98 操作系统启动、触控、真机 | **NOT RUN**。合成文件只含 NHD 头和全零磁盘扇区。 |

对应 [Tab5 原版启动复验](../../README.md) 的后续，使用已发布 Device Service 1.90.0 与同一官方 esp-emu 1.1.0 后端。记录对应真实 ESP32-P4/ESP32-C6 虚拟设备会话。

[执行与复现](report.md) · [机器记录](run.json) · [验证摘要](evidence/98tab5-synthetic-hdd-recognition.summary.json)

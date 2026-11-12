## 现象

2026-11-12 的 26 设备 × 5 固件 M5Burner 批量矩阵中，**Nesso N1（ESP32-C6）5 款固件全部无法进入可用界面**：

| # | 固件 | firmware_id | 版本 | 现象 |
| --- | --- | --- | --- | --- |
| 1 | Launcher | 1897200000000000359 | 2.6.6 Release | 启动后 `assert failed: xTaskPriorityDisinherit`，约 1.3 s 一轮重启循环，无画面 |
| 2 | Meshtastic unofficial | 1897200000000001757 | 2.7.20.79f469c | 有短暂画面后 `Guru Meditation ... (Instruction access fault)`，重启 |
| 3 | Bruce For Arduino Nesso N1 | 1897200000000001876 | 1.15 | 串口停在二级 bootloader `entry`（231 B），无应用输出、无画面 |
| 4 | M5Launcher Arduino Nesso N1 | 1897200000000001205 | 3.0.0 | 同 #1 的 `xTaskPriorityDisinherit` 循环 |
| 5 | Meshtastic RFID Demo | 1897200000000001151 | 2.7.21 | 启动早期反复 `Rebooting...`，无画面前已崩溃 |

同样跑在 C6 的 **NanoC6** 也有 2/5 固件在启动期触发 task watchdog / `delete_entry: task not found`，说明问题不止单个固件。

## 复现

独立会话（非矩阵并发）复跑 Launcher 两次，均稳定复现：

```bash
# Device Service（agent 自有实例，非 8787）
python3 platform/tools/serve.py 18787 --bind 127.0.0.1 \
  --state-dir .work/agent-sweep-20261112/service --max-sessions 12 --max-per-device 6 --session-ttl 2400
# 固件：.work/agent-sweep-20261112/repros/... 见下方 SHA；设备 nesso-n1，runtime=qemu
```

- 固件 SHA-256：`53a01cdde00de8763767d6eefb48965a5d95326b4e88df0f26ad08fe1c00816d`
- 会话：`b318ce1e071c4cdf99cc8d689d35cb84`（178 KB 串口）、`0eb434f1e09f41fc9244e7012109e2e5`（203 KB 串口）
- 两次都在 45–60 s 窗口内完成多轮崩溃-重启，`state=running`（进程未退出）但 guest 无法进入应用。

## 证据（串口摘录）

```
I (…) esp_image: image at 0x200000 has invalid magic byte (nothing flashed here?)
E (…) boot: OTA app partition slot 0 is not bootable
...
auto detect board:23
Failed to mount SDCARD
NVS: Finding keys in NVS...

assert failed: xTaskPriorityDisinherit tasks.c:5156 (pxTCB == pxCurrentTCBs[ 0 ])
Core  0 register dump:
MEPC : 0x40808b76  MTVEC : 0x40800001  MCAUSE: 0x00000002
...
Rebooting...
```

（完整串口在会话目录 `serial.log`；帧证据 `last-frame.png` 为 135×240、非黑 5264 px，只有启动画面片段。）

## 影响

- Nesso N1 目前**无法作为任何 M5Burner 社区固件的可用模拟目标**；UIFlow2 基线之外的应用全部不可测。
- 由于 `state=running` 而 guest 在重启循环，按会话状态判断会得到“运行中”的假象，需要靠串口判失败。

## 期望 / 验收

1. 定位 `xTaskPriorityDisinherit` 与 `Instruction access fault` 的 guest 路径：优先检查 C6 单核 FreeRTOS 调度、互斥量 owner 判定、以及 OTA/NVS 访问后的 flash cache/MMU 行为。
2. 验收：Launcher 与 M5Launcher 能启动到首帧并稳定运行 ≥120 s；Meshtastic 不再出现 Instruction access fault；同轮 NanoC6 回归不退化。
3. 如果确认是固件侧缺陷，也请在 issue 中给出对照依据（同镜像在真机或其它仿真通道的正常表现）。

## 边界

- 全部结果是 virtual-device（QEMU C6）验证，不涉及真机、射频、功耗或电气测量。
- 未修改固件、flash 或设备 profile；使用的是 M5Burner 公开版本原镜像。

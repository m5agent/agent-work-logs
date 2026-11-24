# M5GFX #442：StopWatch 启动时 Type-C USB 选择

- 日期：`2026-11-24`
- 结果：`PARTIAL`（virtual-device validation + host 34/34；真机 Type-C 枚举与热复位路径 `NOT RUN`）
- 工作类型：`pr-review`
- 问题来源：[m5stack/M5GFX#442](https://github.com/m5stack/M5GFX/pull/442)，作者 `hlym123`，英文，OPEN；
  评审前 comments / reviews 均为 0
- 源码版本：`m5stack/M5GFX` PR head `cc6d5ff74783f7b001725a6f758ef11ffa7231aa`
  （base `92bd25c890bb05ea057064401401843e9c9f4f25` = develop tip）
- 环境：macOS arm64 只读源码核对 + ESP-IDF v6.1 本地构建 ESP32-S3 固件；
  本机 Device Service 的 `stopwatch` profile（QEMU，CO5300 466×466，M5PM1 + M5IOE1 已建模）

## 结论

改动方向与实现正确：它把 M5IOE1 GPIO1 / `PYB_MUX_CTR` 从“推挽高”改成“先清锁存、再推挽低”，
位映射与写入顺序都经得起核对。虚拟 StopWatch 冷启动实测：develop 为 `out=0x99`（GPIO1 高），
PR 为 `out=0x98`（GPIO1 低）且 3 秒内稳定，板型识别与 466×466 首帧正常，显示/触摸复位序列不受影响。
host 测试 34/34 通过。

没有发现阻塞合并的缺陷，但提交说明里“高电平断开内置 Type-C 数据线”一句在公开原理图上不成立，
需要作者给出 V1.1 依据；另外后部扩展口默认功能由 USB 变为 UART0，且固件不再有板级路径切回，
需确认是有意为之。

## 关键证据

- 构建或运行：ESP-IDF v6.1，target `esp32s3`，16 MB flash + 8 MB octal PSRAM；
  M5GFX 分别取 PR head 与 develop 两个只读副本，构建同一探针固件
  （SHA256 49ca9f87… / 62b5ceee…）。
- 实机或服务执行：Device Service `stopwatch`（虚拟设备，QEMU）冷启动会话
  `b7aa93bbe0a945c4a4b8405ad97e7ceb`（PR）与 `8cbc44aaaf054d2f863d0540a02ced9c`（develop）。
- 日志、测量或协议：串口 `IOE1_AFTER_INIT mode=0x9D out=0x98/0x99 drv=0x00`；
  466×466 首帧截图（`evidence/frame-pr.png` / `frame-develop.png`）。
- 代码核对：M5IOE1 数据手册第 6 页寄存器表、M5Unified `M5IOE1_Class` 的位映射、
  原理图第 4 页 CH442E 注记、官方 `M5StopWatch-UserDemo` 的 `hal_ioe.cpp:76` 同样写 0。
- host：`sh test/board_detect/run.sh` → 34/34 `passed`。

## 文件

- `report.md`：完整报告（位映射、顺序、影响面、运行证据、与提交说明的差异）
- `run.json`：结构化记录
- `evidence/pr442.diff`：PR 相对 develop 的完整差异
- `evidence/serial-pr-cold.txt`、`evidence/serial-dev-cold.txt`：两版固件的完整串口输出
- `evidence/serial-warm.txt`：热复位变体（二级 bootloader 未继续，模型限制）
- `evidence/frame-pr.png`、`evidence/frame-develop.png`：首帧截图
- `evidence/host-tests-pr.txt`：board_detect host 测试输出
- `evidence/ioe1-register-map.txt`：寄存器语义、位映射与板上网络整理
- `evidence/C152-SCH_Stopwatch_VA_20251201.pdf`、`evidence/m5stopwatch-userdemo-hal_ioe.cpp`：外部依据副本
- `evidence/environment.txt`：构建命令、固件/会话标识与证据哈希

## 未覆盖项

- 真机 Type-C 枚举未验证：本机没有可观察 Type-C 数据通路的 StopWatch。
- 热复位“保留高锁存”路径未跑通：虚拟设备在 `esp_restart()` 后不再继续 boot。
- 虚拟设备没有 USB PHY/复用器模型，只能观察 IOE1 寄存器，不能观察链路本身。
- V1.1 原理图不可得，无法核对提交说明里的电气结论。

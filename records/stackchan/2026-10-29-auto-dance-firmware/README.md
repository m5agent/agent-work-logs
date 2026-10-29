# StackChan 开机自动跳舞固件

- 日期：`2026-10-29`
- 结果：`PASS`（virtual-device）；实体硬件 `NOT RUN`
- 工作类型：`code_change`
- 问题来源：用户要求为 StackChan 编写包含表情、12 路灯效和开机自动舞蹈的固件
- 源码基线：`m5stack/StackChan-BSP@fb5e9f5697803ca64e45fe7ad8eaea3e4100f766`（tag `1.1.1`）
- 环境：macOS arm64；Arduino CLI `1.5.1`；M5Stack Arduino `3.3.10`；QEMU machine `m5stackchan`

## 结论

已完成一套可烧录的 StackChan Arduino 固件。固件启动约 1.5 秒后自动开始
16 秒循环舞蹈，包含 38 个动作/表情关键帧、6 种表情、双轴舵机动作和 12 颗
RGB 灯的同步效果。轻触机身顶部触控区域可重新开始。

同一 16 MiB merged 镜像在虚拟 StackChan 中成功烧录、启动并稳定运行超过
90 秒，完成 5 个自动循环。串口记录 125 个舞步事件；QEMU 数据面记录
1006 个 SCSCL `SYNC_WRITE` 位置包和 1367 次 12 灯 RGB 缓冲刷新。19 张
1 秒间隔、320×240 的虚拟机帧全部不同，未发现致命断言或重启。

首版候选固件在持续舵机应答路径中触发 UART spinlock 断言。最终版本改为
广播同步位置写入（舵机 ID `0xFE`），只读取 BSP 已保存的零位，不再为每个
动作帧等待双舵机应答。修正结果不能外推到实体机械行程、电流、亮度或长期
硬件稳定性。

## 关键证据

- 构建：Arduino `m5stack:esp32:m5stack_cores3` 编译 PASS，应用 570,928
  bytes，程序存储约 18%，静态 RAM 约 9%。
- 产物：merged SHA-256
  `c854d3ac6b958439ad30c5277266575d8765f228febf75de243da5d011904542`。
- 启动：串口出现 `StackChan auto-dance started`，并完成 5 次循环重启。
- 表情：19/19 个间隔帧哈希不同；总览见 `evidence/contact-sheet.png`。
- 舵机：1006 个 SCSCL `SYNC_WRITE` 包，目标内存地址 `42`（目标位置）。
- 灯带：1367 次 RGB 缓冲刷新，共 32,808 个 M5IOE1 RGB 寄存器写。
- 稳定性：超过 90 秒运行，QEMU stderr 的断言/panic/core-dump 标记为 0。

## 文件

- `report.md`：设计、首版失败原因、修复、验证和边界。
- `run.json`：机器可读结果。
- `code/`：Arduino sketch、依赖清单、构建/烧录和舞步校验脚本。
- `evidence/verification-summary.json`：构建与运行证据摘要。
- `evidence/contact-sheet.png`：19 个虚拟机帧总览。
- `evidence/build-summary.txt`：构建命令、资源占用和镜像哈希。
- `evidence/protocol-trace-summary.txt`：串口与 QEMU 数据面计数。

## 未覆盖项

- 未连接或操作实体 StackChan，不声称物理动作、扭矩、电流或亮度已通过。
- 实体机械零位可能因整机装配而不同，首次烧录后需要确认；可用官方
  `HomeCalibration` 示例更新 BSP 的零位。
- 相机、NFC、IR、无线、扬声器和声学效果不在本固件目标内。
- 超过 90 秒的实体长期稳定性 `NOT RUN`。

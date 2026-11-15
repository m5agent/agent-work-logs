# vinylM5Dial 1.0 在 Dial 虚拟设备上无首帧的归因

- 日期：`2026-11-15`
- 结果：`PARTIAL`
- 工作类型：`service_debug`
- 问题来源：固件审查任务 `job-7071ded9a698`（`lane=SIM_PARTIAL`、`status=manual_review`、`error_code=E_NO_FRAME`）
- 源码版本：m5agent/m5stack-esp-emulator `main` @ `55e5763e`
- 环境：Device Service 原生 QEMU，ESP32-S3FN8，`m5dial`（SKU K130），虚拟 Flash 8 MiB

## 结论

未定位到可归因的模拟器模型缺陷，未新开 issue。

同一套板级模型和 QEMU 上，官方 UIFlow2 v2.5.3 Dial 固件可以启动并渲染 240×240 非黑帧
（19,838 B，面板 MADCTL 已写、generation=2）；目标固件的 ROM→二级 bootloader→应用装载
链也已完成，应用仍在运行（UART1 周期性发送 Port B 报文），但从未写面板命令
（MADCTL generation=1、madctl=0），CPU 停在 idle `waiti`，Flash 0 字节变化，也没有
panic、assert 或重启。

因此这不是「模型/外设缺失导致的启动前失败」或「QEMU 断言」型问题；目标应用在显示初始化
之前停住，但停点不可见：该固件的诊断日志走 USB CDC，而 Dial 机器没有把 USB Serial/JTAG
接到会话 chardev。按仓库「无崩溃证据不归因固件、无具体模型证据不开单」的口径，本次只交付
归因边界，不提交模拟器 issue。

## 关键证据

- 目标固件：`vinylM5Dial : mp3 player 1.0`（`dial.bin`，8,388,608 B，SHA-256
  `7778656ee942bb5e87fbc780955c452f752059c9cf9325d7e026b83ec6c7ffaf`），应用描述为
  Arduino lib builder / ESP-IDF v5.5.5，app0 位于 0x10000，SPIFFS 分区未格式化。
- 失败会话：串口 226 B，止于 ROM `entry 0x403c88b8`；帧 248 B 全黑
  （SHA-256 `4bf6fb04707daaa254f0d27219adbb5bfb282a2f495e0bf528cb7ee3efde5832`）；
  `wait` 在 `application_readiness` 阶段超时；事件与快照无崩溃标记。
- 会话内 QOM：`/machine` 下 encoder、pcf8563、ft5x06、rmt0、m5-canbus 均存在；
  QOM diff 只有 pcf8563 时间推进。
- 独立复跑：同一镜像在同一 QEMU 上 PC 反复落在 app0 IRAM 段的 `waiti` 返回点
  `0x40378dda`，`CCOUNT` 正常递增，`CPS`（PS）不在异常/中断上下文；面板
  `generation=1`、`madctl=0`；Flash 前后 0 字节变化。
- 应用存活旁证：UART1 每约 2.7 s 收到 5 字节 `04 fb 01 08 08`；固件自身字符串
  写明 `PORT B RX=1 TX=2 | 9600bps`，与该通道一致。
- 同机对照：官方 UIFlow2 v2.5.3 Dial 固件（8,388,608 B，SHA-256
  `6a0187dad13c491129e9228ca36b9e04adb46ebf9d8d51fca8eca5f9b7332a53`）串口 394 B
  出现应用日志，帧 19,838 B、非黑，SHA-256
  `3116e0ebe6ee1dc60a6a7fe0ece8164a20f4981655df05efc2c1afdc6a96372e`，
  面板 `generation=2`、`madctl=8`。两侧触发相同的 ROM/bootloader 级
  `M25P80` 探测与 `0x10200c` 读取提示，属共同背景，不是差异点。

## 文件

- `report.md`：完整报告（判定路径、复现步骤、边界）
- `run.json`：结构化记录
- `evidence/attribution-summary.json`：脱敏后的观测摘要

## 未覆盖项

- 目标 BIN 在真实 Dial 上的启动与画面：`NOT RUN`，本机没有匹配真机夹具。
- 应用自身 USB CDC 启动日志：`NOT RUN`，Dial 机器未把 USB Serial/JTAG 接入会话 chardev，
  无法读取 `display=` / `displayTask=` / `AudioPlayer startup wait=` 等字段。
- 卡点的外设归属（I2C、SD、I2S 等）：`NOT RUN`，无符号与日志时无法把停点收敛到单个端点。
- 音频播放、SPIFFS 内容、电气与声学行为：`NOT RUN`。

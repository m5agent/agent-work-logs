# Nesso N1 原版 RFID 看门狗与横屏复验

## 背景与目标

在 Device Service 1.89.0 的原生 ESP32-C6 QEMU 上，对原版 Meshtastic RFID Demo 2.7.21 Landscape 执行一轮无追踪长跑和一轮首故障取证。两轮采用相同规范化 Flash，原版两个应用分区读回不变。未连 PN532 对端，未发送输入。 [既有问题](https://github.com/m5agent/m5stack-esp-emulator/issues/216)

## 运行与证据

- 无追踪轮持续 150.021 秒，约 4 秒首次取得非黑帧。USB Serial-JTAG 有两个 ROM banner，第一次为上电，第二次为 `LP_SW_HPSYS`。UART0 有一次重启标记。两轮启动累计四次 PN532 等待超时。
- 独立首故障轮使用同一冻结 C6 运行时与映像。5,000 ms 的首次初始化正常，应用随后尝试设为 90,000 ms 时返回 `0x103`。订阅 IDLE 后第 5,002 个客体 tick 进入看门狗中断。`loopTask` 有 12 次 reset，记录中的 `IDLE.has_reset=0`。
- 两次 UART1 读等待均配置为 1,000 tick，各在 1,002 tick 后以零字节返回，均早于看门狗中断。此轮 PN532 无对端等待按预期超时，原版稳定性判定为 `FAIL`。
- 两份 ZIP 的原始 PNG 都是 135×240，包含同帧顺时针 270°、MADCTL 108 的方向元数据。用冻结源码的 `frame_representation(orient="display")` 离线转换后，240×135 欢迎页与历史长跑和首故障控制的对应 PNG 各自逐字节一致。

## 复验步骤

1. 按清单固定原版 BIN、规范化 Flash、C6 QEMU 和 ROM，每轮使用新隔离会话。
2. 先无追踪采集双串口、画面、原版应用分区读回和停机前 ZIP。用第二轮私有 GDB 有界观察初始化返回、任务喂狗、UART 返回与首个 ISR。
3. 从各自 ZIP 取同帧 PNG 和元数据，在本地按固定源码转换，并核对两个历史控制的帧哈希。结束后确认 Flash 与租约释放。

## 验收与边界

程序持续运行失败，离线横屏回归检查通过。在线 display-orient 导出、RFID 读取、浏览器和实体设备为 `NOT RUN`。Burner 未提交。复验没有变更固件或产品运行时。 [结构化证据](evidence/nesso-current-paired-summary.json)

## 固定源码证据

执行结果和公开数据快照对应同一组固件与运行时哈希。 [主分支验证记录](https://github.com/m5agent/m5stack-esp-emulator/blob/174c6d42048bf12f315e8b572948f17638d0bb77/tests/firmware/esp32c6_mwdt_clock/current-main-rfid-summary.json)

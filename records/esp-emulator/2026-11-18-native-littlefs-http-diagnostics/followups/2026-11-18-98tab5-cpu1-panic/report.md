# 98TAB5 原版启动复位归因

## 背景

先前在 esp-emu 0.50.0 上观察到 98TAB5 单次启动，取帧因没有匹配 ELF 而不可用。1.1.0 的 GT911 与 DSI 配置出现重复软件复位。两轮历史验证同时改变了运行时和板级路径，本次固定 1.1.0，并在同一个 GT911 板型内改变 I²C 器件应答方式。[先前原版记录](../../evidence/tab5-stock-frame-summary.redacted.json)

## 固定输入与执行

Device Service 使用 [`13df3b8a7ab197df14f57d2ca8bc58919a7eb666`](https://github.com/m5agent/m5stack-esp-emulator/tree/13df3b8a7ab197df14f57d2ca8bc58919a7eb666)，API 为 1.89.0。原版 98TAB5 1.3.0 镜像为 9,182,880 字节，SHA-256 为 `ea4fb0889e4a2c68d472947137908c52c25a663152d3ff78262ce2605440dc6d`。规范化后 SHA-256 为 `35c636324ea1fcebd12f4752e458936c2ac151a9d171a67f1d624d944b96b0ff`。原生 esp-emu 1.1.0 SHA-256 为 `633a35f993300a765634ed78a2dbcfd5ffcd5c3f2f354a2dddabeb6108240828`。ROM、eFuse 和 C6 伴生固件均固定在摘要中，guest 应用字节保持不变。[板级对照摘要](evidence/98tab5-gt-board-route-comparison.summary.json)

1. 在独立状态目录和独立监听端启动该版本 Device Service。设置 `M5_TAB5_DSI_EMULATOR`、`M5_TAB5_DSI_BOARD=gt911-ili9881c` 与规范化固件 SHA 的 `M5_TAB5_DSI_FIRMWARE_SHA256S`。加载 Part 的分组另设 `M5_TAB5_GT911_PART`，另一组保留内置识别寄存器。
2. 依次使用 API 的 `/artifacts`、`/firmware/import` 和 `/sessions` 上传、导入和启动同一原版。确认创建的是 Tab5 的 `qemu` 会话，并核对 P4/C6 伴生实例、启动应用偏移和独立 Flash。
3. 两组均自然观察 35 秒，记录串口和原生 DSI 帧。完成后检查同会话 ZIP 的 CRC、清单及各文件哈希，再停止会话，保留历史并释放 Flash 和租约。
4. 在三个新的内置识别寄存器会话中，只用 GDB 硬件断点和读取。前两轮在确认的 `0x400091fe` 核对调用者、`panic_info_t` 和异常栈帧。第三轮先在 `0x4fc02750` 读取 `a0`，记录实际交接地址，然后运行到同一来宾的 `0x400091fe`。脱离调试器后保留后续串口与同会话 ZIP。[异常入口摘要](evidence/98tab5-panic-entry.summary.json)

## 自然启动对照

| 模型 | ROM 启动 | 软件复位 | 转储写入失败 | 完整 DSI 帧 |
| --- | ---: | ---: | ---: | ---: |
| GT911 Part | 19 | 18 | 18 | 0 |
| 内置识别寄存器 | 19 | 18 | 18 | 0 |

两组每次均按 OTA0 从 `0x10000` 加载、尝试转储、写入失败、软件复位的顺序运行。两组录制均未收到 Part 缓冲区溢出或 DSI 读取零值警告。原因归因保持开放。[板级对照摘要](evidence/98tab5-gt-board-route-comparison.summary.json)

## 调试证据

三轮都在 `0x400091fe` 命中转储写入入口，并读到 CPU1 的 `Instruction access fault`，`MEPC=0x0`、`MCAUSE=0x1`、`MTVAL=0x0`。原版应用在 `0x400015ca` 调用该入口，实际保存的调用者返回地址是 `0x400015ce`。ESP-IDF 的异常处理在进入转储写入时已经持有异常上下文。[ESP-IDF 异常处理源码](https://github.com/espressif/esp-idf/blob/v5.5/components/esp_system/panic.c#L378-L386)

精确 rev0 ROM 的次核交接位于 `0x4fc02750`。第三轮实测 `a0=0x4ff00330`，可读入口指令与原版匹配，随后捕获同样的 CPU1 异常。首次调试脚本的字段标签偏移有误，已由保留的异常帧原始字重新解码，后两轮使用更正后的标签。三轮结束前的串口字节与未接调试器的内置寄存器组一致，脱离后都继续复位。[异常入口摘要](evidence/98tab5-panic-entry.summary.json)

## 边界与清理

原版包含 `0xff0000` 起始、64 KiB 的转储分区。报错发生在异常之后的转储写入入口，证据尚不足以定位 CPU1 如何从有效的 ROM 交接走到 `0x0`。两组正常执行和三轮调试均在停止前保留证据，清退 P4/C6 及独立服务，保留终态历史并释放可变 Flash。常驻服务未变更，真机、浏览器和外部网络未验证，未提交 Burner。

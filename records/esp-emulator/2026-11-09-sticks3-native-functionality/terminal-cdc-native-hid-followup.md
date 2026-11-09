# StickS3：PM1 完成输出、原版 AirMouse 与组合回归

本轮在原版固件上修复并验证 [PM1 IAP #201](https://github.com/m5agent/m5stack-esp-emulator/issues/201) 和 [AirMouse BLE HID #203](https://github.com/m5agent/m5stack-esp-emulator/issues/203)，并在同一新构建复验 [Evil monitor #204](https://github.com/m5agent/m5stack-esp-emulator/issues/204)。最终原生 QEMU 重放 126 层，源文件收据覆盖 144 个变更后的文件。QEMU SHA-256 为 `d8f6b447ecd93eab02237d00296704f747da2d8908eb39b6e1c9e76159c755a5`。所有功能结果均为虚拟设备验证。

## PM1 和固定 USB Serial/JTAG

原固件的 PM1 升级已经写入，但旧模型在同一 1 ms SOF 轮询处理中完成 USB IN 事务。跨核空写后，EP1 暂时忙，ISR 已从队列取出尾部内容却不能写回端点；另一条失败路径是 FreeRTOS 补跑 tick 后在同一个 SOF 间隔多次读取并清除状态，原驱动判断临时断开。修复把全速主机 IN 事务与帧 SOF 分开安排。明确选择 CDC 捕获时，来宾调度与 USB 时钟共享指令计数虚拟时钟，450 ms 点按用同一时钟产生。串口日志来自原固件自己的发送数据。

原 PM1 固件在独立构建通过 8/8，在组合构建通过 3/3。每次都实际写入并验证 20,480 字节 PM1 应用，回到地址 0x6e，输出完成标记。破坏 CRC 后保持 0x54、零提交、没有完成标记。关闭捕获时，PWR 长按/短按复现 ROM 下载和恢复 Flash 启动；Bit Pirate 的 USB OTG 独立控制仍通过，主机读取 406 字节并发送 CRLF 得到 ACK。较早的墙钟、诊断和输入路径失败保留在摘要。

[原始候选的八次复跑](evidence/pm1-terminal-cdc-summary.json) · [组合 PM1/OTG](evidence/combined-pm1-otg-summary.json) · [PM1 源码](https://github.com/m5agent/m5stack-esp-emulator/commit/f67218b6b018c238a7b33c0b6a431057d4620512)

## AirMouseS3 原生 BLE HID

原版 AirMouseS3 v1.0 发布 BIN 使用 ESP32-S3 内置控制器，UART H4 不能接到该路径。以已发行 SDK 的机器码和原版应用中的调用及字面量验证原固件的 VHCI 入口和注册回调。QEMU 在来宾正常 FreeRTOS idle 任务的窗口和栈上执行实际回调，避免用宿主嵌套执行来宾回调。另修复 Bumble 的 LE ACL 路由：发送方取已建立连接的地址，防止使用已配置但不属于本次连接的随机地址。

最终组合运行时 4/4 原版会话完成虚拟 SMP、加密、HID 0x1812、54 字节 Report Map、0x2A4D 通知订阅。输入前零报告；实际 BtnA 按下、松开分别由来宾送达 `01000000`、`00000000`。最后一轮 QOM 确认 API H2C 62→65、C2H 86→89、零交付错误。原有 StickS3 UART1 H4 NUS 独立回归仍收到 `ACK:M5_STICKS3_UNIFIED`。先前重置响应交付失败、旧回调调度失败和地址路由失败都保留在摘要。固件 SHA、Flash SHA、运行时身份、对端报告和证据 ZIP 哈希见摘要。

[原版 BLE 和 NUS 证据](evidence/native-airmouse-hid-summary.json) · [BLE 源码](https://github.com/m5agent/m5stack-esp-emulator/commit/26e9e9f5855a0331dbb0daeb4db40e86711640c6)

## Wi-Fi 交叉回归和范围

组合运行时和单独 Wi-Fi 候选各通过管理帧、未加密 QoS 帧、无注入三个会话：来宾 RX、连续 12 条 TX 字节、八帧窗口、复位语义一致。原版 Evil 组合复验在真实 Probe Sniffing 界面再次显示 `m5-fixture-07`，帧哈希与原候选一致；QEMU 有一次 RX DMA 和 IRQ 清除，无新增 TX。组合 Evil 复验没有启用 USB 捕获，先前单独候选的应用 USB 输出仍独立记录。

[组合 Wi-Fi 摘要](evidence/combined-wifi-monitor-summary.json) · [单独 Wi-Fi 实验](monitor-stream-followup.md)

PM1、BLE、Wi-Fi 各自的源码、固件与运行身份分开记录。证据包含按键、来宾数据和清场；公开摘要省略本地路径、执行标识和端点，不上传固件、密钥或原始 ZIP。其他 BLE 构建和运动报告、受保护 Wi-Fi 帧、物理 RF、电气、PM1 物理烧录以及浏览器 WASM 均未验证。

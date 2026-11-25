# 虚拟设备执行

原工作台以裸板加载 Cardputer-Adv 默认 UIFlow2，LoRa 例程报告 SX126x 的 BUSY 超时。候选安排 GPIO3 RESET、GPIO4 DIO1、GPIO5 NSS 与 GPIO6 BUSY，由 ESP32-S3 GPSPI2 连接 SX1262。模型通过模拟命令就绪、真实 GPIO 状态和 SPI 寄存器处理响应。发端的已提交 FIFO 作为有界虚拟包来源，收端须已进入 RX，才接受一次原样传入的数据。[原失败](../2026-11-25-uiflow-camera-and-lora/) · [LoRa1262 接线](https://docs.m5stack.com/en/cap/Cap_LoRa-1262) · [LoRa868 接线](https://docs.m5stack.com/en/cap/Cap_LoRa868)

对每个型号启动两台独立的 Cardputer-Adv 虚拟设备。使用官方 v2.5.3 工作台组合镜像 `b6255f6a…52bd` 和对应两份原 Python。收端实际进入 RX，模型计数为零，原 LCD 没有包。发端键盘输入 `w`、`a`、`s`、`m` 和 Enter，经原例程在实际 SPI TX FIFO 写出 `7761736d`，频率配置字与收端一致。验证器在确认 RX 就绪后原样转交这 4 字节。收端产生 DIO1，来宾通过 SPI 读 4 字节，画面从初始状态更新为 `[0:0:24] -> wasm`。两种型号的两次原例程配对各退出 0，实际 12 个 Worker 全部回收。

运行时 `09eaaac3…7ab3` 是在 0043 已锁定来源上保留原链接参数、重编两个受影响 C 文件的私有增量候选。公开的 0043 源归档仍对应对照，配套候选补丁在本记录。验证为本地 Chromium 浏览器虚拟 SPI/GPIO 和有效载荷。真实天线、频谱、空中时间、电气、正式托管、标准公开工作台的配对入口均未执行。

第一份工具脚本曾将“已加载”误认为客体就绪，未执行原程序即退出。改用客体运行状态、运行收据和原 READY 条件联合判定后的两次有效配对记录仍分别保留原始哈希。详细操作按[候选代码及步骤](code/)执行。

# 运行和复核

在当前静态浏览器 WASM 工作台运行原 Arduino 合并镜像。CoreS3 默认采用 `cores3-wasm-vm-div8`，Cardputer-Adv 采用目标 8 MiB 配置。保留同一来宾记录和停止状态。

原 CoreS3 Wakeup 屏幕已显示触摸唤醒提示。点击 (170,165) 按住约 650 ms 并释放后，QEMU 诊断输出 `model=axp2101 action=off source=reg10-bit0`。工作台收到来宾 SHUTDOWN，中止执行。释放后继续观察至少 45 秒，未见 WAKEUP、第二次 ROM 启动或像素更新。引擎和五个 pthread Worker 已回收。验收需要保留虚拟 RTC 继续计时和 PMIC 恢复，然后观察同一交互流程的重新启动。

CoreS3 RTC 原例程显示 `WiFi Connecting...`。文档占位网络参数未改动，当前浏览器配置为离线。Wi-Fi 和 SNTP 数据面本次不可用，RTC 显示仍需与可复现网络或明确只演示离线设置的版本分别验证。

CoreS3 默认 SDcard 和 Picture 例程没有卡载图片。隔离环境使用浏览器 MEMFS 的固定 64 MiB FAT32 卡镜像，把它交给实际 QEMU SPI SD 设备。相同原始例程先读到卡片，再通过原驱动在 RGB565 绘出写入到 FAT32 的测试 PNG 图案。保留 SD 协议命令和两个真实设备画面。ADV 单独使用固定的最低库版本和 8 MiB，在原 SD 例程中读 28 字节、删除及改名文件并写 1 MiB。浏览器音频和真机电气行为仍待验收。

独立 CoreS3 Arduino Speaker 的 PCM 捕获尝试返回 0 字节，不能据此确认真实播放。默认网页没有声学验收。本记录的原始报告留在本地，摘要包含输入、控制器、帧、身份及清理并省略环境地址。

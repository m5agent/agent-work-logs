# RTC 浅睡证据

- [原版 All day watch 同固件对照](all-day-watch-native.summary.json)记录七份基线、诊断、候选和最终运行时观察及其帧哈希。
- [ESP-IDF 独立探针](rtc-light-sleep-fixture.summary.json)记录同一 GPIO 探针跨运行时复验、候选的 CPU 回执，最终运行时拒绝后清除原因，以及一份独立定时器基线。
- [Device Service 1.87 语义唤醒](device-service-semantic-wake.summary.json)保留原版的按键完成回执、悬停与恢复，以及同会话的最终结果。
- [Device Service 1.87 悬停接管](device-service-suspend-reattach.summary.json)记录控制进程重启、同一来宾接管、GPIO 唤醒和正常清理。

文件是从实际 Device Service 结果、原始串口和 evidence ZIP 提取的有界摘要。网络地址、运行路径、会话 ID 和身份字段均已排除。固件、ROM、运行时、串口和 ZIP 的 SHA-256 保留。ZIP 内清单文件按字节核对，逐项收尾状态来自对应独立会话。

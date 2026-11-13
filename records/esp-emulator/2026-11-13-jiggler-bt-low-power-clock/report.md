# JIGGLER 1.0 的虚拟启动故障

同一份完整 BIN 在 StickC Plus2 虚拟设备启动时无有效应用首帧。默认调度下，两个 CPU 的回溯都进入 FreeRTOS 空闲任务，经空闲钩子等待中断。原 BIN 的 `0x4009400f` 为 Xtensa `waiti 0`。默认计时的直接症状是 CPU1 中断看门狗超时。

使用同一 QEMU、ROM、板型、原始 BIN、虚拟 Flash 准备方式及 10 µs vCPU 时间片上限，只将 `M5_CORE2_ICOUNT_SHIFT` 从 `5` 改为 `auto`。两个独立会话均先触发 `btdm_low_power_mode_init` 的时钟源与分频回读断言，再重启并触发中断看门狗。把时间片上限单独改为 100 µs 时仍触发中断看门狗。一次全量 MMIO 跟踪也捕获中断看门狗，该次未到达蓝牙断言。

对原 BIN 反汇编后，从断言栈地址回溯到蓝牙低功耗时钟配置。该代码设置 DPORT `0x3ff000d8` 的主晶振选择位 26，并回读确认。代码对 `0x3ff000d4` 写入分频值后也回读低 12 位。经典 ESP32 QEMU 的 DPORT 读写分支都缺少这两个偏移，读使用默认零值，写没有相应处理。源选择的回读因此不能通过。这是已确认的模拟器模型缺口。默认计时下的中断看门狗是否由该缺口直接引起，仍需修复后以默认配置复测。

相关地址和寄存器字段见 [ESP-IDF v5.5.5 的经典 ESP32 寄存器定义](https://github.com/espressif/esp-idf/blob/v5.5.5/components/soc/esp32/register/soc/dport_reg.h#L1088)。复现时用 Device Service 上传同哈希的完整 BIN，作为合并镜像创建 `device_id=stickc-plus2`、`runtime=qemu` 的独立会话。对照实例配置 `M5_CORE2_ICOUNT_SHIFT=auto` 与 `M5_CORE2_ICOUNT_MAX_PERCPU_NS=10000`，保留正常看门狗。设备进入 `running` 后每两秒采集串口和帧，直到崩溃或 64 秒。每轮停止本轮创建的会话。

验证仅覆盖虚拟启动。真实硬件、完整 BLE HID 数据面、修复候选和 Burner 提交均为 `NOT RUN`。公开摘要保留固件、运行时和串口哈希，省略内部环境、会话标识和原始跟踪文件。

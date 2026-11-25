# CoreS3 定时关机唤醒的根因与复验

[模拟器 #252](https://github.com/m5agent/m5stack-esp-emulator/issues/252) 来自官方 CoreS3 Arduino Wakeup 例程。原始 16 MiB 合并镜像的 SHA-256 为 `2ddff71f4ceca5e79b709ba823b8ecf0828f2016a85e512df779e526e7a9f295`。在旧锁定 WASM `11c5dea1a3982562c1ccf552df8833e1987cad4cb70cbd3db4f484cd9b230555` 看到原生 320×240 画面上的提示。虚拟触摸 (170,165) 持续约 650 ms，QMP 确认按下和释放，随后收到来宾 `SHUTDOWN` 并退出。等待 45 秒没有新的启动。

在相同旧 WASM 开启 I²C 跟踪，来宾向 BM8563（模型 PCF8563，地址 0x51）写入 `0x0F=0x05` 及 `0x0E=0x82`，配置 1 Hz 的五次倒计时，再通过 `0x01=0x09` 开启电平中断。AXP2101（地址 0x34）收到 `0x90=0x3F`、`0x99=0x00` 和软件关机 `0x10=0x31`，旧模型直接请求退出。CoreS3 原理图的 AXP_WAKEUP 将 BM8563 INT 接到 AXP2101 IRQ，PMIC Power Good 接 ESP32-S3 CHIP_PU。 [官方 Wakeup 例程](https://docs.m5stack.com/en/arduino/m5cores3/wakeup) · [CoreS3 原理图](https://m5stack.oss-cn-shenzhen.aliyuncs.com/resource/docs/datasheet/core/K128%20CoreS3/Sch_M5_CoreS3_v1.0.pdf) · [BM8563 手册](https://www.belling.com.cn/media/file_object/bel_product/BM8563/datasheet/BM8563_V1.1_cn.pdf)

## 修复范围

浏览器 QEMU 源层补丁 0042 在 CoreS3 接通 RTC 与 PMIC。倒计时以休眠时仍运行的宿主时钟推进，TF 置位后通过低有效 INT 驱动 PMIC。原例程先配置倒计时再关机，QEMU 挂起同一来宾。IRQ 保持有效后，PMIC 给出 IRQ 上电原因，QEMU 恢复原 Flash 并执行 SoC 上电复位。未配置定时唤醒的普通关机仍可结束会话。浏览器在挂起状态允许释放已按下的触摸。

此次范围为 Wakeup 用到的电平定时中断。日历闹钟、周期脉冲、物理功耗与精确定时、原生运行时及正式托管发布未执行。可回退源仓库补丁、源锁与浏览器触摸改动，重新构建该版本运行时。

## 复现方式

用 Arduino CLI 1.3.1、M5Stack board package 3.2.5、M5Unified 0.3.0 和 M5GFX 0.3.0，以 `m5stack:esp32:m5stack_cores3` 编译官方 CoreS3 Wakeup 例程合并 Flash。对照只把 `M5.Power.timerSleep(5)` 改为 `M5.Power.powerOff()`，保留同一画面、输入和其它代码。按照模拟器仓库 `scripts/qemu-wasm-build/README.md` 用锁定 Emscripten 3.1.50 构建运行时，用 `platform/tools/build_public_site.py` 重新导出。用跨源隔离的本机静态站在 Chrome 上传各合并镜像，采用默认 `cores3-wasm-vm-div8`，等待原提示稳定三秒后在屏幕原生坐标 (170,165) 按压约 650 ms。

定时版本逐轮检查 RTC TF、PMIC IRQ 唤醒、QMP 挂起和来宾复位及唤醒事件、ROM POWERON、共享帧序号和原画面。观察到完整重绘之后才发下一次触摸。普通关机对照检查 QMP 来宾退出及其后无挂起、唤醒或重启。收尾核对 QEMU 退出码、iframe 和 Worker 回收。

首次候选 A/B 中，第一轮唤醒后 25 ms 内对短暂恢复的旧提示发出第二次触摸。QMP 确认触摸，来宾当时还在启动，随后出现黑屏过渡和完整重绘。该轮未再次挂起，保留为 PARTIAL。后续以完整重绘并稳定的实际画面发送下一次触摸。

## 锁定构建结果

Chrome 158.0.8127.37 执行锁定源构建 WASM `618f471307a11e90301372b5f704afa46df1224be19feda292ba663fb6c31a62`。原始镜像在同一来宾和会话内两次收到 `SUSPEND → guest RESET → WAKEUP`，两次都观察到 RTC Control2 `0x05`、PMIC `source=rtc-irq` 和 ROM `rst:0x1 (POWERON)`。QMP 观察休眠到唤醒两次均为 5003 ms。共享 RGB565 帧序号从 30 到 56、再到 80，画面恢复成相同的提示内容。控制台代次为 0→1→2。两轮共四个触摸边沿均接受。QMP 退出码 0，六个实际 Worker 全部关闭，iframe 移除。

QMP 唤醒出现后，来宾仍要启动和重绘。包含三秒画面稳定条件的端到端观察为 13.725 秒和 13.078 秒。两项时长来自本次浏览器观察。摘要保留了真实标记、帧哈希、源运行时和原始回执哈希，省去完整 UART/QMP、机器路径、端点和会话标识。

普通关机对照镜像 SHA-256 为 `8b0839da632ebe2461886387aeaca9e8fea6394935297f91d4292c4b5913fa37`。同一个锁定 WASM 接受了相同触摸并观察到 AXP2101 软件关机及 `guest-shutdown`。从输入观察 45.758 秒，仅此一条机器事件。退出码 0，iframe 移除，实际 Worker 六个全部关闭。

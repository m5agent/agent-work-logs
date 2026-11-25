# 同原固件复验

三次正常工作台会话使用 [USB Serial/JTAG 源修复](https://github.com/m5agent/m5stack-esp-emulator/pull/267) 中同一完整锁定 WASM 和无跟踪的导出。Cardputer-Adv 采用 `cardputer-adv-wasm-wallclock`。加载默认 `USB CDC On Boot: Enabled` 的 Arduino 原例程固件 `07ebcecd…c0e7`，没有改动示例代码或 Arduino 选项。

每次在 ROM entry 后留出约 2.5 秒并通过实际页面执行 F12（G0）按下和释放。工作台独立 USB Serial/JTAG 控制台显示 `Button A Pressed`、`Button A Released`，同一客体的 USB 控制器从 251 字节/10 包到 288 字节/18 包。三个真实按压时长约 106–111 ms。三次运行均退出 0，六个 Worker 全部退出并移除 iframe。

另外用不变的 WASM/固件启用已经存在的 GPIO 跟踪。实际来宾执行 GPIO 输入寄存器读取并得到 GPIO0 `1→0→1`；独立 USB 控制器增量及消息与标准工作台相同。这条带跟踪正控另存，不与标准工作台三次结果合并。

初次候选曾复现 `Stack canary watchpoint triggered (ipc1)`，另一轮启动后无应用输出。两种失败继续保留。三次复验覆盖锁定版本的原 Button USB 功能。更广的冷启动条件、负载和物理 USB 仍待验证。[更早的 ROM 与候选失败对照](../2026-11-25-cardputer-adv-usb-cdc/)

## 重跑

1. 按 [锁定 USB 构建记录](../2026-11-25-cardputer-adv-usb-cdc/) 导出相同站点。完整 WASM `ee110d208e358de4eeafa2583ecfbbc3f505dc0568bf85a25ca3c84a63f3cc60`。
2. 使用 Arduino CLI 1.3.1 和 M5Stack Arduino 3.2.5 默认选项，验证官方 [Button 原例程](https://docs.m5stack.com/en/arduino/m5cardputer/button) 的 4 MiB 合并 BIN，摘要见本记录。选 Cardputer-Adv 和浏览器运行，加载固件。
3. 选 USB Serial/JTAG 输出。就绪后在工作台聚焦设备，用 F12 按下并释放 G0。记录控制器回读、客体 USB 输出和正常 Stop。
4. 若复跑诊断，在隔离导出的 Engine 启用现有 `M5SW_GPIO_TRACE=1` 与 `M5SW_GPIO_TRACE_PIN=0`，保持运行物及固件相同。检查三个来自实际 IN0 读取的 GPIO0 转变。

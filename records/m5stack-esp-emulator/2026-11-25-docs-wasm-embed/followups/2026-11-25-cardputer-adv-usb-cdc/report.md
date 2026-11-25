# 验证和复现

改动将现有 S3 USB Serial/JTAG 控制器数据面接到 Cardputer-Adv 的浏览器执行。设备经过真实 CDC IN FIFO、端点完成和虚拟主机调度。工作台把该输出独立于 UART 控制台，保持原 REPL/输入接口。候选以源码锁完整构建，并在合入 UART2 定位后的工作台使用相同 WASM 再导出复验。

| 固件 | 浏览器虚拟设备验证 |
| --- | --- |
| 原 IR NEC Arduino | 来宾 USB 输出 `Send now: address=0x1111, command=0x34`，随后 `0x35`。独立控制器计数 435 字节、42 包。原生 RGB565 有三个不同的非黑帧，工作台平面竖屏显示文字倒置并裁切。尚未验 GPIO44 的 NEC LEDC 波形。 |
| Button 关闭 CDC 对照 | 实际 G0 按下和释放，UART0 显示对应原例程标记。USB 控制器维持 251 字节、10 包，来自启动期 ROM 输出。 |
| Button 默认 CDC 原版 | 先前同一 WASM 的两个浏览器会话均未收到原应用标记。第一次重现历史的 `ipc1` 栈观察点异常，第二次启动后保持安静。默认 Button 问题未关闭。 |

每个执行到来宾的测试正常停止，退出码 0，实际 6 个 Worker 均回收。验证限本地浏览器虚拟 USB 输出和 UART0 输入对照。USB 主机向客体的数据、物理 USB、电气、红外脉冲、正式托管未执行。

1. 以候选提交 `a5a48eceee172be037fe7c742eeff5f529f778d5` 执行 `scripts/qemu-wasm-build/build.py` 的锁定全量构建。核对补丁 0044、完整 WASM `ee110d208e358de4eeafa2583ecfbbc3f505dc0568bf85a25ca3c84a63f3cc60` 和 ROM 及站点摘要。
2. 在 Arduino CLI 1.3.1 使用 M5Stack Arduino 3.2.5 的 `m5stack:esp32:m5stack_cardputer`。编译文档 [IR NEC](https://docs.m5stack.com/en/arduino/m5cardputer/ir_nec) 和 [Button](https://docs.m5stack.com/en/arduino/m5cardputer/button) 的原始例程，使用记录中的镜像。另用相同 Button 源码显式关闭 CDC 作为对照。
3. 在本地导出的标准工作台选择 Cardputer-Adv 和浏览器运行，上传相应合并 BIN。IR 在下拉选择 USB Serial/JTAG，核对相继出现的两条地址和命令，再读取固定控制器状态。采集实际 240×135 帧和平面显示方向。Button 对照选 UART，用实际 G0 按下和释放，核对两条日志。用同样操作复现默认 CDC 的记录。
4. 下载每次运行的证据，记录固件、启动参数、设备侧输出和清理状态。区分独立 USB 与 UART 视图。

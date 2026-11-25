# CoreS3 和 Cardputer-Adv Arduino 文档 WASM 预研

2026-11-25 的浏览器 QEMU WASM 虚拟设备验证。26 个直达 Arduino 例程均已编译并检查合并镜像布局与 SHA-256。默认浏览器结果与隔离原型取证分别记录。

| 设备 | 构建 PASS | 默认 WASM PASS | PARTIAL | FAIL | NOT RUN |
| --- | ---: | ---: | ---: | ---: | ---: |
| CoreS3 | 15 | 4 | 6 | 5 | 0 |
| Cardputer-Adv | 11 | 0 | 2 | 9 | 0 |

默认路径已验证 CoreS3 显示绘图、BarGraph、触摸与电源键。传感器和摄像头能提供可见画面，输入变化仍需随例程验证。浏览器启动用时是在研究主机观测的单次值，文档页面的性能验收仍待独立测量。

### 已复现的差异

- Cardputer-Adv 的较新库组合把设备识别为 StampS3。将 Flash 显式设置为 8 MiB 仍复现，按文档最低版本固定库后，显示、键盘和带预置介质的 SD 样例可在隔离环境运行。原型结果已分别每例绑定，不外推到其余 Cardputer-Adv 例程。 [兼容性 issue](https://github.com/m5agent/m5stack-esp-emulator/issues/245)
- CoreS3 默认浏览器附件仅接 PIR。原 Unit Relay 和 Ultrasonic-I²C 例程分别存在缺继电器状态、I²C NACK 并显示 4500 mm 的情况。同一固件与 WASM 二进制在隔离站点搭载真实虚拟外设后，屏幕与 GPIO 输出或距离事务同步变化。 [附件 issue](https://github.com/m5agent/m5stack-esp-emulator/issues/246)
- CoreS3 RTC 使用文档中的网络占位符运行到 `WiFi Connecting...`。完整演示需要可配置的 Wi-Fi 与 SNTP 对端。CoreS3 Wakeup 本应在点击后经过五秒虚拟定时唤醒，实测触发 PMIC 关机与 guest shutdown；释放后 45 秒仍未唤醒。 [RTC 原例程](https://docs.m5stack.com/en/arduino/m5cores3/rtc) · [Wakeup 原例程](https://docs.m5stack.com/en/arduino/m5cores3/wakeup)

### 范围和证据

直接 Arduino 范围包含 23 个正文 sketch、CoreS3 的 BarGraph、Cardputer-Adv 的库内 display 和版本固定的 SD WAV 播放。英文正文用于构建，三语正文的代码词元已比对。CoreS3 79 页附件教程共 136 个例程，Cardputer-Adv 两页附件教程共 10 个例程。两项 CoreS3 代表附件已执行，其余附件单列。ESP-IDF 和 UIFlow2 另行归档。

- `PASS` 表示文档行为由同一 guest 的可观察结果支持。`PARTIAL` 表示看到了原例程的部分行为，仍缺关键输入、输出或配置证据。`FAIL` 表示已运行但当前默认浏览器体验未达到教程所述行为。`NOT RUN` 表示快照缺少原例程的 guest 启动回执。
- [Arduino 矩阵、构建、输入和证据哈希](arduino-matrix.summary.json) · [JSON Schema](arduino-matrix.schema.json) · [隔离原型和版本对照](prototype-controls.summary.json)
- 重建时使用 M5Stack Arduino 板包 3.2.5 和矩阵记录的固定库版本，按页面原样提取 `.ino`。CoreS3 使用 `m5stack:esp32:m5stack_cores3`，Cardputer-Adv 使用 `m5stack:esp32:m5stack_cardputer` 的默认 4 MiB 工具选项。独立 8 MiB 校验的 FQBN 与依赖版本见原型对照记录。
- [CoreS3 Arduino 文档](https://docs.m5stack.com/en/arduino/m5cores3/program) · [Cardputer Arduino 文档](https://docs.m5stack.com/en/arduino/m5cardputer/program)

浏览器屏幕、虚拟外设读回与软件计数的结论只适用于记录中的固件和配置。真机、声学、射频、电气和机械特性为 `NOT RUN`。

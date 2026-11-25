# Arduino 原例程复现

用 Arduino CLI 1.3.1、M5Stack Arduino 板管理器 3.2.5 和固定库版本编译英文文档中的原始代码块。Cardputer-Adv 选择文档中的 M5Cardputer，M5Cardputer 库 1.2.0、M5GFX/M5Unified 0.3.0。使用默认板选项生成完整合并 BIN，通过当前浏览器 WASM 工作台运行，用 QEMU 真实来宾串口、RGB565 数据、实际输入回执与停止结果对照。

## Cardputer-Adv

运行 [Display](https://docs.m5stack.com/en/arduino/m5cardputer/display) 的合并镜像。启动进入来宾后，UART 出现 `Keyboard: Unsupported board type: 136`（M5GFX 0.3.0 枚举为 StampS3），随后 `IntegerDivideByZero`、黑屏及复位。对应 ELF 的 PC 落在使用屏幕宽度计算绘图坐标的循环。运行 [Keyboard](https://docs.m5stack.com/en/arduino/m5cardputer/keyboard) 则画面持续全黑；已发送数字键、字母键和编辑键中的测试序列，QEMU 接受的键事件不能代替来宾文本变化。当前运行时可补查原生路径已有的 Cardputer GPIO 面板及键盘检测补丁是否适合浏览器源层。验收要求原显示和键盘例程在目标机型上分别绘出动态图形和可编辑终端。

## CoreS3 Unit

- Unit Relay 原例程在来宾画出开关。两次对同一开关位置的触摸实现 Open→Closed→Open，三个RGB565哈希对应状态变化。浏览器配置仅提供已支持的 PIR 装配，未挂载继电器，也未验证控制引脚实际切换。
- Unit Ultrasonic-I2C 原例程持续报告 I2C NACK，同时屏幕显示固定 4500.00 mm。M5Unit-Sonic 0.0.2 的失败读取进入回退值。验收应在原接线和 Wire 路径提供设备地址 `0x57` 的 ACK，并对两个注入距离产生两个对应来宾读数和更新后的画面。

浏览器的原固件验证与原生 Device Service 独立。硬件、电气与超声波测量 `NOT RUN`。脱敏摘要保留固件、ROM、WASM、画面和回收结果，共享地址和 Worker 标识已省略，会话标识已哈希化。

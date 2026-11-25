# 版本与端口的原例程验证

## Arduino 与 CoreS3 Unit

Cardputer-Adv 的 [Display](https://docs.m5stack.com/en/arduino/m5cardputer/display) 和 [Keyboard](https://docs.m5stack.com/en/arduino/m5cardputer/keyboard) 使用文档中最低允许的 M5Cardputer 1.1.0、M5Unified 0.2.8、M5GFX 0.2.10，以及显式 8 MiB。完整合并固件由同一浏览器 WASM 执行，显示动画和键盘输入均可见。A/B/C、退格、回车共 10 个实际事件，终端提交 `ab`。相同 8 MiB 配置、较新的库复现板型探测错误。这个组合支持固定版本演示，默认新版库故障仍由 #245 跟踪。

挂接 CoreS3 Port A 的 Ultrasonic-I2C 时，实际 I2C 地址 0x57 数据通路随 QOM 从 1000 到 250、1700，再回到 1000 mm。连续读取的事务计数和读字节数增加，屏幕显示相应读数。挂接 CoreS3 Port B 的 Relay 时，同一画面位置的两次点击使 LCD 呈现 Open→Closed→Open，实际 GPIO9 Relay 模型读回 false→true→false。使用默认浏览器机型配置的对应失败对照已保留。两个候选各使用原始固件与同一运行时，区别在于明确的附件声明和受限输入。正式的文档例程挂接还需要入口与生命周期。

## UIFlow2 v2.5.5

官方 CoreS3 v2.5.5 的原应用段保留，隔离来宾只组合浏览器编程需要的 LittleFS 启动文件。用浏览器上传完整镜像后，原显示例程的 `rotation 0` 读回 320×240，并画出完整 100 像素二维码。对照的 v2.5.3 工作台报告 240×320，画面在边缘裁切。v2.5.5 对照走普通 CoreS3 上传的慢时钟执行配置。默认 UIFlow2 工作台和已有固定例程仍各自绑定版本。

官方 ADV v2.5.5 的原应用段同样保留。文档中的基本用法 `from cap import NFCCap; NFCCap()` 在实际固件 guest 中报告 `TypeError: unexpected keyword argument 'chip'`。精确完整示例在 v2.5.3 报相同构造错误。v2.5.5 的完整原例程未稳定到达该构造，单独的最小构造证明版本中的 SDK 接口问题。没有执行物理 NFC 或卡片数据读取。

摘要中记录实际固件与 WASM 哈希、控制器或串口和来宾像素，以及正常 Worker 回收。环境地址和同会话直接标识均已省略。

# Dial 原版快转的同一虚拟时钟对照

两次在隔离 Device Service 1.88.0 运行未改的 8 MiB 原版 vinylM5Dial 1.0 R1F30，与同一七轨 AudioPlayer 夹具交互。每轮交错运行九个 35 ms 和九个 5 ms 动作。固定的 QEMU 诊断构建 V2 使用 QEMU_CLOCK_VIRTUAL 记录相位边界、来宾 GPIO_IN1 实际读回、选中的 LCD 转换和来宾 UART 索引命令。输入仍走 Device Service 的 encoder 接口。记录器通过 M5SW_DIAL_TIMELINE 启用。会话 ZIP、串口、240×240 画面及清理回执均已读回。[固定接口](https://github.com/m5agent/m5stack-esp-emulator/blob/210c7bcca94c9066f7b839778db25519376879df/docs/device-service.openapi.yaml)

| 运行方式 | 35 ms | 5 ms |
| --- | --- | --- |
| 1.88 发布构建，无追踪，两次启动 | 18/18 | 14/18 |
| 诊断构建 V2，两次启动 | 18/18 | 17/18 |

V2 第二轮一次 −16 格输入的 64 个有序边沿均完整到达，期待曲目 7，来宾 UART 选择曲目 1。一个 GPIO 相位长 7.187 ms，其间 GPIO_IN1 读取数为零。该相位前后实际读取的间隔为 10.901 ms。该相位内有 30 次选中 LCD 写入，面板回调累计 0.437 ms。两轮 V2 合计四个未读取相位均有 LCD 活动，同批其余三个所在动作仍选曲正确。[逐动作时间线摘要](evidence/dial-188-v2-correlation.summary.json)

这些读回证明在一次选曲偏差中出现了完整边沿与来宾漏读相位，说明输入排程和来宾采样应分别验收。窗口中的 LCD 累计执行时间仅覆盖所查回调，无法解释完整读取间隔。诊断构建与发布构建的漏选比例也有不同，两组样本不足以确定采集改变量或 LCD 因果关系。测试只运行隔离会话，保留历史且释放 Flash，两轮租约归零。真机、浏览器、Burner 与诊断构建发布保持 NOT RUN。

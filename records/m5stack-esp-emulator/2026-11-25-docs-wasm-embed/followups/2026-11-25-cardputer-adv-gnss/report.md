# 验证和复现

原版本可运行两个 GPS 程序，但没有进入来宾 UART2 的定位语句，屏幕停在初始数据。本修复在 Cardputer-Adv 的固定 UIFlow2 v2.5.3 工作台新增明确的「LoRa Cap 定位」启动环境，给该会话附加 UART2 QEMU 字符设备。UART0 编辑器继续独立。两个按钮从固定、带行校验和的 GGA/RMC 数据供给 UART2，来宾解析和刷新自己的屏幕。[原始失败及 LoRa 无线状态](../2026-11-25-uiflow-camera-and-lora/)

| 操作 | UART2 回执 | 客体 LCD 文本 |
| --- | --- | --- |
| 地点 A | 6 条 NMEA 语句，合计 423 字节实际读入 | 48.1173 / 11.516667 / (12, 35, 19) |
| 地点 B | 6 条 NMEA 语句，合计 423 字节实际读入 | -33.859 / 151.2099 / (16, 33, 47) |

两份官方 Python 使用独立新来宾，同一会话中的两次实际按钮事件匹配两张 240×135 RGB565 帧。普通工作台对照未创建第三串口，实际键盘输入 `a`、`2` 被官方板型例程经原串口依次读回。三次会话分别正常退出，6→0 个 Worker，移除 iframe。说明覆盖虚拟 UART 控制器及客体解析。物理电气路由、天线、定位精度、正式托管和 SX1262 无线收发均未执行。

## 复现

1. 从代码提交 `42dd0b8cfb4fc0a259cdde76e0d25a2ae47d9a1c` 按 `docs/pages-deployment.md` 本地导出工作台。使用锁定 WASM `e350ed7b2f969139803befef12757178049427058a212136868d382dfe5a5f4b` 及相同的 ROM；源构建见[锁定记录](../2026-11-25-cores3-qvga-camera/evidence/locked-build.summary.json)。
2. 选择 Cardputer-Adv、浏览器运行、参考固件和「LoRa Cap 定位 · UIFlow2 v2.5.3」。标准工作台组合镜像为 `b6255f6af5ad10236380eae09a76b44ca174b5c4de391aef16413bdc590952bd`。浏览器此次从各自已核验的缓存读取官方 ROM 与基础固件响应。
3. 分别启动新会话，将 [LoRa1262 GPS](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/lora1262/cardputer_adv_lora1262_cap_gps_example.py) 和 [LoRa868 GPS](https://github.com/m5stack/uiflow-micropython/blob/a61a29409f09f1f4bebae05e15c4bd6dcc4956b6/examples/cap/lora868/cardputer_adv_lora868_cap_gps_example.py) 的原源码导入编辑器并运行。等待客体屏幕准备，再点击地点 A，核对经纬度和时刻，随后点击 B 重复。
4. 每次保存运行收据，核对 UART2、动作、字节数及客体帧摘要。中断程序并停止来宾，核对正常退出和回收。另用普通启动环境运行官方 Cardputer-Adv 按键轮询示例，复现键盘和无定位的对照。

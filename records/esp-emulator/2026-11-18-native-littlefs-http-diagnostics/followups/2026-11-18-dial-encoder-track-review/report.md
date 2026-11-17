# Dial 原版快转与选曲审核复核

## 原版 R1F30 无插桩复跑

在两个独立冷启动中，将原版 vinylM5Dial R1F30 与七首索引曲目的 AudioPlayer U197 / N9301 PORT.B 附件配对。Device Service 源码固定为 `929dbf749e4a8ecd6c469fce8aea44120febd03f`，使用同一未插桩原生运行时。每轮启动后等待有效 UART 命令确认曲目 1，再按记录表执行带符号短转和整圈。每次操作分别核对控制器完成格数、GPIO 边沿总数和新增的校验和有效 N9301 选曲命令。

| 边沿间隔 | 短转选对 | 整圈选对 | 合计 |
| --- | ---: | ---: | ---: |
| 35 ms | 6/6 | 12/12 | 18/18 |
| 5 ms | 5/6 | 9/12 | 14/18 |

36 次操作均取得每格四个边沿。较早插桩试验另行观察到原版在快转时的来宾采样缺口。对原版 IROM 的回读确认构造时设置 A=GPIO41、B=GPIO40，两次注册均返回零，执行了寄存器轮询分支。无插桩复跑复现选曲遗漏，能测交付总数，未测逐边沿时序或单次漏采。轮询间隔为何拉长仍未定位。 [无插桩证据](evidence/r1f30-uninstrumented.summary.json) · [原版来宾 GPIO 读回](https://github.com/m5agent/m5stack-esp-emulator/blob/929dbf749e4a8ecd6c469fce8aea44120febd03f/docs/evidence/2026-11-18-dial-fast-rotary/original-pair-summary.json) · [固定 M5Dial 参考实现](https://github.com/m5stack/M5Dial/blob/533c9d0198e72621d55a4d35f726d3d53a7e1431/src/utility/Encoder.h)

## 公开 R1F27 源码对照

用同一份公开应用、PlatformIO 6.1.19、Arduino-ESP32 3.3.11 / ESP-IDF 5.5.5 分别构建原库和单文件 IRQ 注册改动版。后者新增 GPIO40/41 的 IRQ 函数符号。两份重建固件在同一原生运行时都通过 5 ms 整圈 6/6、35 ms 整圈 6/6、短转保持曲目 2/2。首次探索误用 R1F30 的每格选曲预期，发现两个应用版本行为不同后停止，未计入这组对照。该测量未显示 5 ms 提升，原版 R1F30 也没有被替换。 [公开应用源码](https://github.com/Layer812/vinylM5Dial/tree/d9d2af725412df9554bc1bf154efff8a541adf15) · [构建和运行摘要](evidence/r1f27-rebuilds.summary.json)

## 早期审核基线

早期候选 `412b47d7392af6fc3526eb5887c3fe82cbf69f3d` 的首次顺时针动作都以 UART 光标 0、Unit 默认曲目 1 开始判定。留存 UART 显示首次索引命令之前还有 22 字节的初始化通信。实际得到同一索引时，更改期望值就出现过 `PASS` 和 `FAIL`。这些首次动作没有已经开始播放的基线，保留其原判定作为审核缺陷证据。 [早期审核摘要](evidence/reviewer-early-baseline.summary.json)

## 最终 Reviewer 复跑

Reviewer API 合约为 `0.17.0`，执行源码 `22569f70b6121f7eab263cf0364855b228497f79`。每个有曲目断言的动作先确认同一会话已有有效播放命令与稳定曲目，继续核对控制器和来宾生命周期，然后在提交前再次采样 UART 光标。如基线变更，该动作保留 `PARTIAL` 并且不提交。接口的布尔接受回执表示排队，交付另由完成格数和完整边沿数判定。应用层在基线后的 UART 中比对校验和有效的索引命令和稳定的曲目索引。

| 复跑 | CW 结果 | CCW 结果 |
| --- | --- | --- |
| 正向 | +3 / 50 ms，12 边沿，预期 4，实测 4 | −16 / 35 ms，64 边沿，预期 2，实测 2 |
| 刻意错误期望 | +3 / 35 ms，12 边沿，刻意期望 5，实测 4 | −2 / 35 ms，8 边沿，预期 2，实测 2 |
| 原版快转 | +16 / 5 ms，64 边沿，期望 3，实测 2 | −16 / 5 ms，64 边沿，期望 7，实测 7 |

六个控制器动作均通过交付核对。正向复跑是 `SIM_VERIFIED`。两个反例会话都返回 `E_SIM_ENCODER_TRACK_MISMATCH` 并保留人工复核。独立回读三个同会话 ZIP 的清单、UART 与串口摘要，验证六个选曲命令的偏移和校验和。曲目断言按七首曲目环绕，保持与实际索引的比较范围。两种反例各自保留输入参数和实测值。 [最终源码复跑摘要](evidence/reviewer-final-sourcebound.summary.json)

最终 Reviewer 测试 247 项通过，使用 Python 3.9 启动器。模拟器最新证据文档固定于 `ca07fbba4c16877ec857d4cf9a36085f05568802`，相对执行时的 `929dbf74…` 只有文档变更。GitHub CI 的平台合约和网络命名空间策略均通过。 [模拟器正式证据](https://github.com/m5agent/m5stack-esp-emulator/tree/ca07fbba4c16877ec857d4cf9a36085f05568802/docs/evidence/2026-11-18-dial-fast-rotary) · [GitHub CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/44202285287)

## 验证范围

当前结果覆盖原生虚拟设备中的 GPIO 边沿总数和 UART 数字曲目索引。物理旋钮特性、浏览器 WASM、PCM 播放和 Burner 提交未执行。这里的行为结论来自原生隔离复跑。

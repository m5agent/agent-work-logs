# Dial 原版轮询、GPIO 边沿与选曲指令

三次完成的独立冷启动都运行原版 vinylM5Dial 1.0 R1F30 `7778656ee942bb5e87fbc780955c452f752059c9cf9325d7e026b83ec6c7ffaf`，Device Service 1.98.0 源码 `dffe87fd60ef34b0c65ddaf7e46ab73fa224d16d`，PORT.B N9301 七轨索引夹具。每轮快速输入都从第 6 轨开始。普通会话和诊断会话均禁用网卡、保留同会话证据 ZIP，结束后无活动租约，Flash 已释放。[固定 Device Service 源码](https://github.com/m5agent/m5stack-esp-emulator/tree/dffe87fd60ef34b0c65ddaf7e46ab73fa224d16d)

| 独立执行 | 8 ms 正向 16 格 | 默认 35 ms 归位 | 5 ms 正向 16 格 |
| --- | ---: | ---: | ---: |
| 发布二进制 `38549673…`，无追踪 | 9/10 | 10/10 | 未执行 |
| 诊断二进制 `0a4d21d0…`，两次冷启动，只读 GPIO 指令观测 | 22/22 | 23/23 | 1/4 |

发布版再次出现同一个行为。控制器交付完整 64 条 GPIO 边沿，来宾发出有效索引指令 `04fb030600070f` 并选择第 7 轨，预期第 1 轨。发布会话缺少 GPIO 读取时序。先前 1.97 的原版 8 ms 失误保持独立证据。[前次普通冷启动](../2026-11-18-dial-197-original-cadence/README.md)

诊断二进制的 22 次 8 ms 操作在虚拟时钟上测得边沿间隔 8.035–13.439 ms。固件相邻轮询间隔可达 11.725 ms，所有相位此次均被两个原版 GPIO 读取指令覆盖。

诊断中的三次 5 ms 失败均交付正序的 64 个边沿，分别有 3、3、2 个完整相位没有任何 `GPIO_IN1` 读取。这些窗口前后的实际原版轮询间隔为 6.096–7.411 ms。用原版指令 `0x4204de12` 和 `0x4204de1b` 的 GPIO41/GPIO40 读回重放原版状态表，三个失败动作各为 +56 计数，理想值为 +64。+56 对应 14 格，在七轨夹具上仍为第 6 轨，实际也没有新索引指令。第四次 5 ms 操作同样漏读一个相位，状态表仍得到 +64 并选对。整个诊断 5 ms 组的实际虚拟边沿间隔为 5.058–10.425 ms。[逐动作证据](evidence/dial-r1f30-198-pc-comparison.summary.json)

5 ms 的失败已定位到来宾实际采样及原版计数。8 ms 发布版的优先排查仍是同场 GPIO 相位采样及其任务等待区间。有效 UART 指令已指定实际选中的曲目；先前显示写入与部分未读窗口同窗，绘制、驱动等待和宿主调度的各自影响仍待定位。[此前同原版 5 ms 寄存器对照](https://github.com/m5agent/m5stack-esp-emulator/blob/dffe87fd60ef34b0c65ddaf7e46ab73fa224d16d/docs/evidence/2026-11-18-dial-fast-rotary/original-pair-summary.json)

## 复现

1. 使用原版 BIN、固定原生运行时和独立 `dial` Device Service 会话，挂 PORT.B 七轨 AudioPlayer。按默认 35 ms 将实际选中的曲目设为 6，再发 `{ "kind": "encoder", "delta": 16, "edge_period_ms": 8 }`。逐步核对控制器 `gpio-edges`、有效 N9301 UART 数据和实际曲目。
2. 在单独会话使用既有只读 GPIO PC 诊断二进制和逐动作回执的 8/5/35 ms 序列。同步记录真实相位边沿和两个原版读取点，按实际返回值逐相位重算计数，与新 UART 索引比较。混合测试中，固件没有改变曲目时继续使用已有的第 6 轨前置状态。
3. 校验同会话证据 ZIP 的 CRC、清单、来宾帧及实际固件指纹，停止并确认 Flash 和租约已释放。首次混合验证的归位断言在曲目未变时提前结束并正常清理。修正夹具后另跑完整会话。

实际旋钮、浏览器、物理发声和 Reviewer 入口未执行。未提交 Burner。

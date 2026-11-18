# 同原版 Dial 的 GPIO 交付与 UART 选曲

Device Service 1.97.0 绑定源码 `8fea7bb182afc0094b8c42461673459bb8f1d965`，实际 Xtensa QEMU SHA-256 `38549673557129d5e9e0100ce9de6539b261b834e9960523b2400dfa110c61b5`。三次独立冷启动都上传同一份原版 vinylM5Dial 1.0 R1F30，SHA-256 `7778656ee942bb5e87fbc780955c452f752059c9cf9325d7e026b83ec6c7ffaf`。QEMU 禁用网卡，运行时未启用 GPIO、SPI 或指令追踪。PORT.B AudioPlayer U197 提供七轨索引夹具。[设备服务源码](https://github.com/m5agent/m5stack-esp-emulator/tree/8fea7bb182afc0094b8c42461673459bb8f1d965)

| 同版独立执行 | 5 ms | 8 ms | 12 ms | 20 ms | 默认 35 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| 两次冷启动，各 20 个 ±16 格整圈 | 8/8 | 7/8 | 8/8 | 8/8 | 8/8 |
| 第三次冷启动，历史短转和整圈共 18 个动作 | 9/9 | · | · | · | 9/9 |
| 先前两次未追踪的历史混合动作（保留） | 14/18 | · | · | · | 18/18 |

第二次冷启动第 18 个动作是 `+16 @ 8 ms`。初始第 6 轨，按七轨取模预期第 1 轨。控制器交付 64 条 GPIO 边沿，AudioPlayer 仍在播放，实际接收一条校验通过的 N9301 索引指令 `04fb030600070f`，选中第 7 轨。三次会话没有坏 UART 帧，均取得不同的 240×240 非黑帧；结束前保存同会话证据 ZIP 并核验 CRC 与文件清单，停止后 Flash 与租约均已释放。[本轮逐动作回执](evidence/dial-r1f30-197-cadence.summary.json)

历史只读追踪把三个 5 ms 整圈漏选绑定到原版实际未读到的 GPIO 相位。本轮从 GPIO 边沿计数与有效选曲指令定位了 8 ms 漏选，未采集 8 ms 下的来宾 GPIO 读指令时间。结果把明确观测到的漏选扩到 8 ms。样本内 12、20 ms 的通过不构成平稳阈值，默认 35 ms 保留。[先前同原版 5 ms 对照](https://github.com/m5agent/m5stack-esp-emulator/blob/8fea7bb182afc0094b8c42461673459bb8f1d965/docs/evidence/2026-11-18-dial-fast-rotary/uninstrumented-original-summary.json) · [实际 GPIO 读回历史](https://github.com/m5agent/m5stack-esp-emulator/blob/8fea7bb182afc0094b8c42461673459bb8f1d965/docs/evidence/2026-11-18-dial-fast-rotary/README.md#原版实际读取-gpio-的复验)

## 复现

1. 用原版 BIN 在独立 Device Service `dial` 原生会话冷启动，挂载 PORT.B AudioPlayer 七轨夹具。等待实际自动播放第 1 轨。
2. 使用标准 input 端点发送 `{"kind":"encoder","delta":16,"edge_period_ms":8}` 或回执中的其他正负序列。省略 `edge_period_ms` 走默认 35 ms。每次等待控制器交付 detent，核对 `gpio-edges` 增量和 AudioPlayer 实际新收到的有效索引 UART 指令。
3. 保存同会话帧和证据 ZIP，核对来宾 Flash 指纹。用 `purge=0` 停止，确认没有活跃租约并关闭独立服务。

实体旋钮、浏览器、实际音频解码及发声、Reviewer 审核入口均未执行。未提交 Burner。

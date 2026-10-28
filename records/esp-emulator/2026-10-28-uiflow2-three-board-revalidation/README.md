# ESP Emulator StopWatch / StickS3 / Core2 UIFlow2 三设备接口复测

- 日期：`2026-10-28`
- 结果：`PARTIAL`（核心 SDK/协议接口与共享候选修复通过；模型边界、候选固件重建和物理硬件仍保留）
- 工作类型：`code_change` + `virtual_device_validation` + `report`
- 问题来源：用户要求并发复测 StopWatch、StickS3、Core2 当前 UIFlow2 接口并统一处理共性问题
- 源码版本：[`m5agent/m5stack-esp-emulator@f311c7e0ede2ab98bf05ca8c89c64607575734e3`](https://github.com/m5agent/m5stack-esp-emulator/commit/f311c7e0ede2ab98bf05ca8c89c64607575734e3)
- 环境：macOS arm64；UIFlow2 v2.5.3；28-patch ESP32 QEMU runtime；全部结果为 `virtual-device validation`

## 结论

三块板均完成 system runtime、socket、MQTT、网络、HTTP、EasySocket、EzData、Modbus、ESP-NOW 控制面、
输入和可用 UI 路径复测。确认并提交五个 hash-pinned 共享源码候选修正：

- `0002`：`requests2.urlencode` 保留字符和 UTF-8 编码；
- `0001`：M5UI Canvas triangle、M5Image float scale 和 M5Spinbox integer step 的原生参数 marshalling；
- `0021`：BLE 32-bit advertising UUID 解包；
- `0022`：Modbus TCP→RTU frame 的非法默认构造；
- `0023`：MicroPython 不存在的 `Loop.sock_recv`。

候选源码在同一虚拟设备路径上通过，但原厂冻结固件没有被替换。物理硬件、RF、声学、光学和电气测量均为
`NOT RUN`。

## 关键证据

- 稳定通过：每台 system runtime `50 PASS + 1 STATE_PASS`、sockets `23/23`、MQTT `42/42`、
  network `14/14`、EasySocket `57 PASS + 1 N/A`、EzData `17/17`。
- HTTP stock 三台均为 `15 PASS / 1 FAIL`；`0002` 候选编码路径三台 `2/2`。
- Modbus stock 三台均为 `42 PASS / 8 ERROR`；`0022 + 0023` 候选三台 `50/50`。
- StopWatch/Core2 的 M5UI 同 VM stock→candidate 对照证明 Canvas/Image/Spinbox 修复。
- StopWatch 最终候选复跑为 `4 STATE_PASS + 2 FRAME_PASS`；三角形中心像素在容差内。
- 完整平台回归 `1344` 项 `OK`，仅 `1` 项既有 skip；四个生成器检查和 `20` 项文档契约通过。

## 文件

- `report.md`：完整结果、根因、剩余边界和复现方式
- `run.json`：结构化记录
- `evidence/results-summary.json`：三设备分母、失败和阻塞汇总
- `evidence/regression-summary.txt`：源码和文档回归摘要
- `patches/`：BLE UUID32、Modbus transform 和 Modbus async socket 最小修正

## 未覆盖项

- StopWatch `drawPixel` 的单像素 CO5300 窗口缺陷仍存在。
- `QRCode.setText` 与 TLS epoch 已有候选 patch，但本轮未重建对应候选固件。
- StopWatch/StickS3 `playWavFile` 路径仍挂起；Mic 无非零 PCM 输入 fixture。
- ESP-NOW TX/RX/IRQ 仍被 OpenMAC vendor-action peer 路由缺失阻塞。
- Core2 host-key callback 稳定性、完整 28 类文档方法矩阵和文字 glyph OCR 仍需补测。
- 未执行物理硬件验证。

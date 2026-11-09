# 实现与验证

## CoreMatrix 的官方启动

未修改的 UIFlow2 v2.5.4 在初始 C61 诊断后端进入 Wi-Fi 初始化后卡住。0x600ad800 一直读零，PHY 驱动的超时轮询无法完成。实现按虚拟时钟运行的 WDEV 计数和 PHY 校准命令完成状态，客体随后能退出 Wi-Fi 初始化。C158 原厂板型探测还使用 GPIO0/1 软件 I²C。修正 IOE1 的 LED 供电位，模拟 HP I²C 命令批次状态和 USB Serial/JTAG RX、IRQ、TX 包提交，原镜像能以真实驱动显示未配置 SSID 的 36 像素叉号。原生隔离 Device Service 的 12 像素绘制、九个 PM1 按键状态和串口 216 字节输出均有单独证据。

## 浏览器运行时

Xtensa 浏览器源锁加入初代 Cardputer 和两款 Paper，复用同一帧和 Worker 桥。RISC-V 独立源锁编译 ESP32-C61，并按正式机器身份选择 ROM、WASM 和 USB 控制台。最初裁剪后的 C61 构建缺少 is25lp128 闪存器件。补齐后，SHA 压缩器返回值与 WASM 回调签名不匹配，修复保留原压缩实现。浏览器初步测试随后显示原厂图案，USB REPL 画出精确 12 像素区域并核对 A/B/C，正常退出和实际 Worker 回收。旧失败作为独立试验保留。

官方 CoreMatrix 2.5.4 允许 PSRAM 不存在时使用片内内存。当前测试覆盖这一配置。Quad PSRAM、真实 Wi-Fi 数据传输、物理设备和电气时序另行验收。ROM、固件和可变 Flash 留在独立测试缓存。

## Paper 和初代 Cardputer

两款 Paper 的 ET047TC1 使用 540×960 黑白数字画面。PaperS3 触控沿真实 GT911 I²C 和 GPIO IRQ 路径运行。模型在有触点或待上报松手时安排扫描，保留未读报告直到客体 ACK。第一次在 UIFlow2 打印 ready 后立即操作时，实际 QMP 已收下按放，客体直到约 7.9 秒后才输出首个轮询心跳。第二次等待实际轮询心跳后，仍用同一 250 毫秒目标操作，原 M5 API 报告 `(270,400)`、松手及恢复，六个 Worker 全部回收。首次失败另外保留，包括其引擎 Worker 未在 CDP 清理期限内退出。

PaperS3 Factory V0.5 的 300 毫秒操作未得到目标图标。按原生测试同样的 500 毫秒操作复验，未命中位置保持基准，命中位置的蜂鸣器图标区变化 607 像素。PaperDIY 的 Factory V1.0 来自原始应用源码并使用已完成工厂首次关机流程的 NVS。A/B 各改变自己区域 533 像素，松手恢复。两款 Paper 的官方基底工作台分别通过 63 项编辑器和 26 项固定示例。一个独立 PaperS3 试验复现了启动 PIF，不能从本轮正向结果推出启动可靠性或实时时延。

初代 Cardputer K132 在独立的 8 MiB Flash 板型上执行 Factory V0.9 与 UIFlow2 v2.5.4 原镜像。Factory A 键打开启动器，Fn 图标与实际模型按放一致。UIFlow2 原镜像在完成 Offline 画面后接收 F12 并进入 Develop。Factory 的动态右侧图标使一次全区域哈希断言失败，重验使用与目标操作直接相关的 SCAN 区域和独立 Fn 图标精确像素。完整报告保留原始观察。

使用源码部署指南构建并导出两套 WASM 后，可重放下列独立用例。固件路径指向从对应公开来源取得并通过 SHA-256 校验的本地文件。

```sh
M5_PUBLIC_SITE=.work/public-site M5_PUBLIC_QEMU_OUT=.work/papers3-factory-500 \
  M5_QEMU_UPLOAD="$PAPERS3_FACTORY" M5_QEMU_DEVICE=papers3 M5_QEMU_PAPER_STOCK_HOLD_MS=500 \
  node platform/tests/test_public_qemu_paper_stock_guest.mjs
M5_PUBLIC_SITE=.work/public-site M5_PUBLIC_QEMU_OUT=.work/corematrix-official \
  M5_QEMU_UPLOAD="$COREMATRIX_OFFICIAL" node platform/tests/test_public_qemu_corematrix_stock.mjs
```

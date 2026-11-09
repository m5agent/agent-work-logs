# StickS3：原版 Evil 混杂收包和有序发送捕获

[#204](https://github.com/m5agent/m5stack-esp-emulator/issues/204) 的原版应用验收已走到 Probe Sniffing 的实际数据面。旧的 AP 扫描证据与本次混杂模式实验分开保留。

原生 QEMU 的 StickS3 测试模式保持 Wi-Fi 控制器的 RX DMA 和 IRQ 路径，同时允许校验通过的无保护三地址 QoS 数据帧。控制器读取每个 TX DMA 描述符后，在改写帧之前保存完整字节；`raw-tx-window` 以复位为边界提供最近八条序号和字节，`raw-tx-latest` 继续可用。序号缺口表示采样遗漏。该路径没有主机网络后端，guest 请求不会转发或通过 RF 发射。

在独立 Device Service 中上传原版 Evil-StickS3 v1.5.1-beta 镜像（SHA-256 `84582c9b4179b11a6d7fc1e918731e44b066f24ea7fbbfe6f9516a910c44b653`），启用 `wifi_monitor_fixture=raw`。从实际画面选择 Probe Sniffing，进入 Stop Sniff 菜单后等待结果列表稳定。注入一条 46 字节的合成 Probe Request。应用的 USB Serial/JTAG 输出 `Probe Sniffing Started...`、`Found: m5-fixture-07`；帧缓冲显示 `1.m5-fixture-07`。QEMU 记录了 RX DMA、IRQ 及 guest 清除中断，注入前后 TX 序号均为 11。无注入复跑进入同一个 Stop Sniff 画面，显示列表保持为空，无 RX DMA 交付或 guest IRQ 清除。该次 USB 就绪标记未观测到，串口就绪单独保留为 `PARTIAL`。

SDK 回归分别发送管理帧和无保护 QoS 数据帧，guest 回调收到的字节与注入相同。SDK 每次发出 12 条无害请求；及时轮询观察到 1–12 的所有 53 字节发送缓冲，延后读取只保留 5–12，与八帧容量和序号缺口一致。坏 FCS 和 Protected 位输入被拒绝。发送捕获是 DMA 请求缓冲，包含 SDK 的占位字节。

复现命令和固件构建入口见项目 [StickS3 monitor 回归](https://github.com/m5agent/m5stack-esp-emulator/tree/6660c8767dae2adab8abb99c8314c9eef9248e51/tests/firmware/sticks3_wifi_monitor)。用专用服务和隔离状态目录运行该目录的 `run_test.py`，指定本轮构建的 SDK 夹具，分别运行接收、空注入、普通 AP 及关无线电控制。原版 Evil 则按上述真实按键流程采集 QOM、帧和证据 ZIP 后以 `purge=0` 停止。原始 ZIP 不随记录公开；下方摘要保留哈希，省略本地路径、会话标识和端点。

虚拟设备验收覆盖已测试的管理帧和无保护 QoS 数据帧、原版应用解析和有限发送窗口。受保护帧、四地址、控制帧、物理信道行为、RF 和攻击效果未验证。回滚本次 PR 即退回单帧发送捕获和无 QoS 的收包范围。

[公开证据摘要](evidence/monitor-stream-summary.json) · [本次源码](https://github.com/m5agent/m5stack-esp-emulator/commit/6660c8767dae2adab8abb99c8314c9eef9248e51)

# PaperS3 GT911 报告时序与 Core2 受控 STA

## 模型变更

隔离候选从模拟器提交 `65f40eac4521ceb2af9962298e1a26a6e07aae78` 起步，模型变更提交为 `0cf118851cf97dd8c63fc6ad0027856a929e4751`。活动接触期间一次未读报告继续锁存。来宾清除 `0x814e` 后，候选沿既有扫描相位调度下一次到期，跳过已经历的扫描周期。周期取配置寄存器 `0x8056` 低四位加 5 ms，定时器以 QEMU 虚拟时钟计时。

Goodix 编程指南 §3.2 说明报告周期字段。§5 说明坐标读回与清除缓冲状态，并描述未及时读取时按周期重发中断脉冲。这次候选的可验收范围为清除之后的报告相位和配置周期。 [Goodix GT911 Programming Guide，2014-08-04 Rev.00](https://community.renesas.com/cfs-file/__key/communityserver-discussions-components-files/256/GT911-Programming-Guide_5F00_v0.1-_2800_4_2900_.pdf)

## 原版对照

两组各使用独立 Device Service，加载同一 PaperS3 Factory V0.5 原版和归一化后的 16 MiB 虚拟 Flash。等待 `board_M5PaperS3` 与稳定的原版蜂鸣器区后，以 (113,347) 为坐标按相同顺序注入 12 次 150、300 或 500 ms 接触。两组均接受全部输入。以稳定区域改变 607 像素为图标切换，冻结版为 9/12、候选版为 7/12，剩余样本图标零变化。两个原版组均为 `PARTIAL`。这组结果没有建立模型变更改善原版响应的证据。

另一个带只读跟踪的候选执行同一原版，先正向和反向拖动，再长按。正向读取起、终点与三个中间坐标，反向读取起、终点与两个中间坐标，两个拖动均随后读到 `0x80`。长按连续读到 `0x81`，松手后读到 `0x80`。跟踪运行时独立记录 SHA-256。拖动和长按验收覆盖 GT911 来宾读回，图标切换采用前两组的单独判据。 [原版和探针的逐次摘要](evidence/papers3-native-gt911-scan-phase-summary.redacted.json)

## 独立 I²C 回归

两组使用相同 ESP-IDF v5.5.4 探针并运行真实虚拟 I²C 控制器。探针向 `0x8056` 写入并读取低四位值 15，按下期间从每次清除到下个就绪报告计时。此探针将 9 ms 设为区分阈值。冻结版 0/8 达阈值，读取间隔 4.447–6.003 ms。候选 8/8 达阈值，间隔 18.757–20.510 ms。两个运行时均先读到松手报告 `0x80`，再清除并读取空闲状态 `0x00`。该结果验证本模型中的配置报告间隔及保留相位路径。

五次原生运行均先保存证据 ZIP，再停止并释放虚拟 Flash，活动租约为零。复核逐一回读 ZIP 摘要、ZIP 清单中的固件身份和原始摘要中的停止状态。

## Core2 Linux 原生受控 STA

Core2 采用 `m5core2`、`qemu-wifi` 和 `core2-openmac`，在 Linux ARM64 私有网络命名空间中执行同一份受控 ESP-IDF 来宾夹具。外层容器禁用网络，隔离规则默认拒绝入站和出站，宿主无外部路由。实际 Reviewer 方法链运行规划、会话准入和终态输运收集，来宾串口独立报告 `dns_a=1 dns_nxdomain=1 udp=1`。最终捕获为一次 DHCPv4 DORA、三条带双向负载的 UDP 流。独立收据将传输标记为 `OBSERVED`。完整审核队列和整单结论为 `NOT RUN`。

同固件负向对照把二进制 UDP 回包最后一个字节改掉。两个 ZIP 中的最终捕获都保留 DNS A、NXDOMAIN 和双向 UDP，回包只有末字节不同，来宾独立报告 `udp=0`。这条对照区分协议流量转发与应用接受结果。缺少命名空间能力的计划在分配租约前返回 HTTP 503 和 `network_isolation_unavailable`。两次有来宾运行的会话均停止并释放 Flash，活动租约为零。

真实审核执行版本 `697913308ec2fb24c5a8be8d50f9fcb3170875c2` 与 Reviewer 提交 `755b275c7973d1c2b51ecaf26584b259d53071c8` 的源码树均为 `d0d67c989c3881332e57f1d63618263aaead524b`。审核套件 197 项通过。范围为受控 IPv4、DNS 和 UDP 夹具。原版 Core2 云端应用、HTTP、WPA2、IPv6、浏览器和物理 RF 均为 `NOT RUN`。 [Core2 双向输运和负向对照](evidence/core2-native-contained-sta-summary.redacted.json)

## 适用范围

该对照聚焦原生虚拟触控器的报告时序与固定原版的图标响应。浏览器、物理触控、实际 INT 波形与电气时序均为 `NOT RUN`。模拟器 main 为 `c53750bf0cc23e717943c6c3c79e49b11e1a227a`。完整本地平台套件运行 2,395 项，跳过 10 项，其余通过。最早的 Core2 候选套件有一项 API 验证清单元数据不一致，已更新清单并重新跑过集成验证。51 项文档检查与范围、运行覆盖、外设目录、QEMU 配置和项目快照校验通过。模型变更可以通过撤回对应源码提交回滚。 [模拟器主线](https://github.com/m5agent/m5stack-esp-emulator/commit/c53750bf0cc23e717943c6c3c79e49b11e1a227a)

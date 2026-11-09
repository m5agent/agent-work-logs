# Classic 烧录与 StickS3 审查复验

源码基线 `dfd2f0fc539a87c68771e93dc3b06a758acebf71`，候选 `4b1dbc8bea1b79a7e1cf5ce3e26a67a3c0982e61`。

## #178 Classic ESP32 烧录

使用复现问题的同一 QEMU `27df1b40…`、esptool 5.6.0 和既有 11 台设备
夹具各跑三轮。原有尺度 16/8 的有界重试得到 23 PASS
和 10 FAIL。失败包含 ROM MEM_DATA 校验、UART 流中断、
写入超时以及一条写入通过后的 guest marker 缺失。调低倍率 4 和 2 仍复现问题。
以指令计数控制时钟的早期配置已观察到真实 `OHAI`，但完整传输超过原预算，
两个不等待首个 UART 连接的对照还缺 ROM banner。

候选只在 stock stub 下载 VM 先等待串口观察连接，再用单线程 TCG 的固定
`icount shift=4` 控制 UART 节奏。实际 esptool 上传和写入、完整 Flash 逐字节
比较及应用启动的验收保持。候选 33/33 通过全路径，
33/33 完整 Flash 读回。其中一例使用原有的有界重试。候选期间主机
一分钟负载 10.36–28.25。独立 Atom Lite 服务复验观察真实按键 down/up
串口、取证及停止清场。Canonical 118 的同模型独立复验和 host-image 对照分列。
[逐轮摘要](evidence/classic-uart-summary.json)

## #199–#204 StickS3 固件矩阵

#199 的第二个输入走真实 B 键，逐键使用同长度的无输入对照。只响应 B 的 guest
夹具在 A 后保持同帧，B 后出现预期帧。#200 保留首个非黑帧后的 0、5、10、30 秒
观察。M5Launcher 的主菜单与启动动画可区分，持续动画负控得到 PARTIAL。
没有显式 guest readiness marker 的通用样本把 application_ready 保持为 false。
M5Gotchi 的一次并行 QEMU 退出及单独复验均保留。
[输入与采样证据](evidence/sticks3-input-and-readiness-summary.json)

#201–#204 的原样本完成基线和修复后对照。PMIC Upgrade 发出真实 PM1 I2C
升级请求但未完成，Bit Pirate 保留 TinyUSB 安装失败，AirMouseS3 缺 BLE HID
对端，M5Gotchi 和 Evil-StickS3 缺验证用的 Wi-Fi monitor 数据面。
矩阵返回具名 `PARTIAL/runtime_model_gap`。安静串口与空扫描结果不能独立归因，
精确样本用实际上传 SHA 绑定。PulseOS 是未命中缺口的对照。选择按 issue
允许的结构化缺口方案处理误判，控制器能力在 RUNTIME-10 逐项跟踪。
[虚拟设备证据](evidence/sticks3-gap-summary.json)

## #206 完整 Flash 重放

原版 M5Gotchi v0.7 冷启格式化 LittleFS 并写入配置。取已停止会话 A 保留的完整
8 MiB Flash，经既有 merged 上传入口创建隔离会话 B。保留首个 35 秒未达 marker
的结果，随后同一快照重放和独立新 A/B 均读到配置。超大镜像 HTTP 413，错误上传
SHA HTTP 409。新增文档说明按尺寸、SHA 和相同设备核对，快照 ID 仍供原 diff
入口使用。[完整证据](evidence/flash-replay-summary.json)

## 开放边界

- #188 的同一 Tab5 v2.5.4 在稳定 0.51.0 等待 DSI PHY lock。1.0.0-rc2
  在原始固件及两组探针镜像上触发同一非法指令，固件 Python、UI 和触摸未验收。
  [五次独立复验](evidence/tab5-188-summary.json)
- #192 的最新 QEMU 在自然高负载下通过 StackChan 与 Core2 AXP192 定向并发；
  两轮完整 68 用例未完成。保留触及负载保护的中止和独立 StickS3 输入失败。
  [并发复核摘要](evidence/peripheral-192-summary.json)
- #205 是新增取帧方向能力。现有 `frame.png` 返回面板坐标帧，需要从实际
  MADCTL/玻璃装配映射获取可信方向，再设计和验收兼容的输出字段。源码审查，未新增接口。

候选全平台运行 2052 项，跳过 8 项。初次本地全量的
三项文档失败来自新增 RUNTIME-10 后未同步导航与状态表，补齐后全量复验通过。
项目生成检查和 PR scope 通过。完整原始包、固件、Flash 与会话身份留在本地。

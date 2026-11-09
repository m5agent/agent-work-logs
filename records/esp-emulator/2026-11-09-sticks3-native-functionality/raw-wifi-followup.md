# StickS3 原始 Wi-Fi 帧与 PM1 输出复测

## 隔离原始帧夹具

源码 de64a5f39127b43499a4476d38237bf4dbe17be4 的原生 123 层运行时 SHA-256 为 9d61d807ee821990361fba074920a2ece2d8b32dbdc002f2be5c1dbad7256309。通过 Device Service 的 wifi_monitor_fixture=raw 启用夹具，服务在 guest 启动前核验一块虚拟 NIC 且没有宿主网络后端。

向控制器的 raw-rx-mpdu 写入 42 字节管理帧，ESP-IDF promiscuous 回调逐字节读到相同内容并确认 RX IRQ。SDK 发送无害 Probe Request 后，从 raw-tx-latest 读取实际 TX DMA 的 47 字节及对应序号。错误 FCS 在同一会话先被拒绝，随后正确帧通过。无注入的独立会话无回调与 TX 捕获。旧 QEMU 在创建会话前拒绝 raw 请求。原有 beacon 正负对照同样通过，证据在停止前留存。 [原始帧验证](evidence/raw-wifi-summary.json)

原版 M5Gotchi 和 Evil 的扫描证据继续使用各自精确固件与运行时。Evil 混杂模式、受保护及 QoS 帧、连续 TX 捕获、真实 RF 和攻击行为仍待验收。

## PM1 最后一次打印

在默认和单线程 TCG 的两次原版失败中，guest 均完成 RUN 后的 I²C 探测、进入最终打印并返回。随后读到 I²C 空闲、USB EP1 可写且 SOF 持续变化，证据流缺完成字节。通过运行也可短暂进入 HWCDC 的断开分支并恢复，无法据此判定失败根因。以虚拟时间补齐 SOF 的候选在三次 Device Service 复跑中两次通过，一次仍缺完成日志。该实验未随原始帧夹具交付。 [PM1 指令及控制器复测](evidence/hwcdc-postrun-summary.json)

## 合并与验证

本地平台套件执行 2,064 项，无失败，10 项跳过。最终 PR head 7819aec8534503cdba46b44f328f4bfcde0bbdce 保留同一原生补丁和 API 源码，合并提交为 02c046679fd7c7dbb008afd3c4c29e3cfca517df。PR 和合并提交的远端平台及网络隔离检查均通过。#204 保留开放，等待原版 Evil 混杂模式与扩展捕获验收。 [PR #212](https://github.com/m5agent/m5stack-esp-emulator/pull/212) · [PR CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42594949609) · [main CI](https://github.com/m5agent/m5stack-esp-emulator/actions/runs/42595383751)

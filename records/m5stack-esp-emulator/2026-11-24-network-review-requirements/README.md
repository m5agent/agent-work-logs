# 模拟器网络审查能力需求（对应 issue #238）

- 日期：`2026-11-24`
- 结果：`REVIEW`（需求与验收标准；模拟器/审查服务实现均未开始）
- 工作类型：`infra_baseline`（网络审查能力规格）
- 问题来源：用户要求“看看要不要修改模拟器，如果需要提出需求”；近 27 条审查中
  11 条网络相关转人工
- 源码版本：`m5stack-esp-emulator` 当前 main（需求基线）；审查服务运行时
  `contract_version=0.5.0`
- 环境：macOS arm64；常驻审查服务；本机 Device Service 原生 QEMU；Linux snapshot
  worker 仅准入 `cardputer_adv_pronunciation` / `core2_2048`；无真机

## 结论

近 27 条任务中 **11 条**因 `E_NETWORK_PARTIAL` 转人工，是最大的人工来源。它们不是
固件失败，而是当前审查链路拿不到可判定的同 guest 网络证据：

- 7 条 `worker_namespace_unavailable`
- 3 条 `board_not_advertised`
- 1 条 qemu-wifi `PARTIAL`（web server 需要先按住 B）

审查服务要求“原生 STA + Linux 网络命名空间”；本机 Device Service 在 macOS，无法提供。
但设备目录里 Cardputer / Cardputer-ADV **已经公布**
`native_network.sta={runtime:qemu-wifi, profile:generic-observe, http_post_fixture:true,
tcp_fixture:true}`，说明一部分能力已经存在，缺的是**可移植的审查级网络后端 + 结构化证据**。

已向模拟器仓库提交需求
[#238](https://github.com/m5agent/m5stack-esp-emulator/issues/238)，核心要求：

1. **P0 portable review-sta**：`qemu-wifi` 同 guest、不依赖 Linux namespace；
   虚拟 AP + DHCP/DNS/HTTP/TCP/UDP/MQTT fixtures，无宿主 egress，pcap；
2. **P0 setup inputs + events**：同一 guest 先执行 hold/按键/触摸，再等待网络事件；
   返回 `events`/`assertions`/失败码，审查侧可直接 PASS/FAIL，不再用空 45 秒窗口；
3. **P1 板卡覆盖**：Cardputer/ADV、StickS3、StopWatch、PaperDIY/PaperS3、Tab5 C6、
   StickC Plus2/Core2；不支持的板卡在 capability 明确标 unsupported，不能转人工；
4. **P1 控制固件**：每板 known-good（DHCP/DNS/HTTP）、known-bad（错误 WPA2）、
   setup-required、no-network 四类对照；
5. **边界**：真实 RF 攻击、LoRa/Meshtastic、NFC/红外/真实手机等标
   `external_dependency`，不要用网络人工复核掩盖。

## 关键证据

- 窗口统计：27 条任务中 11 条 `E_NETWORK_PARTIAL`（7 namespace、3 board、1 qemu-wifi）。
- 设备目录：Cardputer/ADV 有 `native_network.sta` qemu-wifi/generic-observe；StickS3 有
  `qemu-wifi/uiflow2-sticks3-wifi`；StopWatch 只有 unified；PaperDIY/PaperS3/Tab5 无通用网络。
- 现有文档：`docs/device-service-api.md` 的 qemu-wifi、native STA、HTTP/UDP/TCP fixtures、
  SoftAP 章节。
- 需求全文见 issue #238；审查侧过程诊断见
  `records/firmware-review-service/2026-11-23-review-process-diagnosis/`。

## 文件

- `report.md`：完整需求、优先级与验收标准
- `run.json`：结构化记录
- `evidence/network-review-summary.json`：脱敏后的网络人工统计

## 未覆盖项

- 模拟器实现与验收：`NOT RUN`（本单只提需求）。
- 通用 Linux worker / 便携 userspace 后端：`NOT RUN`。
- 11 条网络任务的重跑：`NOT RUN`。
- 真实 RF、LoRa、NFC、手机配网等外部依赖：`NOT RUN`。

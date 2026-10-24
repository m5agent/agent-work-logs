# ESP Emulator three-lease Core2, guest IPv6 and current backlog

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device + docs/contract）
- 工作类型：`code_change`
- 问题来源：用户要求完整整理当前代码、文档、已完成工作和剩余待办
- 源码版本：`m5agent/m5stack-esp-emulator @ fa66e1849756346946f3a6acf88757ac55d2c525`
- 环境：macOS Apple Silicon、Linux arm64 network namespace、补丁 QEMU、Device Service、UIFlow2 StickS3 test build；无物理硬件

## 结论

两份此前仍开放的虚拟设备门禁已经关闭：

1. Core2 `core2-native-hci` 由 3 个独立 artifact-bound lease 各完成
   `121/121` 次 scan/connect/NUS GATT/disconnect；三轮 firmware、ELF、
   QEMU 和工具哈希一致，WiFi/公网、frame/QOM、pcap、evidence、cleanup、
   bounded TCG 和 HLI health 全部 PASS。
2. 同一 UIFlow2 StickS3 test-build guest 在 Linux private namespace 内取得
   controlled AAAA，完成 allowed IPv6 HTTP，denied-port 被 nftables 阻断，
   pcap、namespace cleanup、DNS/HTTP fixture close 和 QEMU reap 同轮 PASS。
   `NET-06` 已从 Backlog 移除；原厂 UIFlow2 默认 IPv6 能力仍未声明。

文档已按职责重新收敛：`project-status.md` 只维护当前能力，
`project-backlog.md` 只保留未完成工作，`workstreams.md` 不再复制动态计数，
`validation-ledger.md` 保留日期证据，代码地图、API/OpenAPI 和专题页同步更新。
文档一致性测试新增旧口号回归拦截。

## 关键证据

- 平台套件：`355/355 PASS`；文档契约：`19/19 PASS`；Node：`2/2 PASS`。
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot 和
  compileall：全部 `PASS`。
- Core2 聚合 evidence：
  [reconnect121-3x](https://github.com/m5agent/m5stack-esp-emulator/blob/fa66e1849756346946f3a6acf88757ac55d2c525/tests/uiflow2/core2_native_hci/evidence-2026-10-25-hci4-reconnect121-3x.json)
- IPv6 namespace evidence：
  [ipv6 namespace AAAA/HTTP PASS](https://github.com/m5agent/m5stack-esp-emulator/blob/fa66e1849756346946f3a6acf88757ac55d2c525/tests/network/ipv6_end_to_end/evidence-2026-10-25-ipv6-namespace-aaaa-http-pass.json)
- CI：run `40125359517` 在 `a4ef8b8` 上成功，最终 `fa66e18` 的 run
  `40125476618` 也成功。

## 文件

- `report.md`：改动、验证、当前工作和剩余 Backlog。
- `run.json`：结构化结论。
- `evidence/verification-summary.json`：脱敏机器可读摘要。
- `patches/`：不适用；网络测试 patch 与 Core2 evidence 均在源码仓库。
- `code/`：不适用；可重建入口见源码仓库 `tests/network/ipv6_end_to_end/`
  和 `tests/uiflow2/core2_native_hci/`。

## 未覆盖项

- bit-exact ESP32 BT controller/baseband、物理 cache/PSRAM 和 RF；
- Core2 长时吞吐、并发和 process-stop/teardown；
- 物理硬件同固件 SHA 验证；
- CIDR/domain-set、worker 自动发现、跨主机 QEMU executor/reattach；
- 当前刷新后的 AtomS3R/PaperMono 四固件 Device Service 功能重跑；
- 运行态 ACL/许可、生产 secure boot/Flash Encryption/eFuse key 流程；
- C6 Zigbee、Core2 legacy I2C routing 和 ATECC608 三个 runtime gap。

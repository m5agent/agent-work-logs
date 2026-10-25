# Core2 fixed-icount five-instance cold start

- 日期：`2026-10-25`
- 结果：`PASS`（仅 virtual-device validation）
- 工作类型：`code_change`
- 问题来源：Core2 五实例 no-stagger ACK/delivery 失败 follow-up
- 源码版本：`m5agent/m5stack-esp-emulator @ 39e6295`
- 基线：`3d1484c`
- 环境：macOS arm64、Python 3.13、Node.js、项目补丁 QEMU；未使用物理设备

## 结论

默认 Core2 QEMU 调度从自适应的 `icount shift=auto` 改为固定
`shift=5,align=off,sleep=off`，并让测试 BLE server 在 WiFi 和持续 PSRAM
负载前初始化。两批独立、零错峰的五实例 `5×120s` Device Service 门禁均为
`5/5 PASS`，合计 `10/10`。每个 lease 在同一 guest 内通过 WiFi DHCP/HTTP、
公网 DNS/HTTP、外部 NUS GATT、frame、31 节点 QOM、pcap、evidence 和
14–15 次 1 MiB PSRAM 全缓冲读回。

此前 `shift=auto` 的一批 `5/5 PASS` 和独立 `3/5 FAIL` 继续保留为历史对照。
本结果关闭五实例 120 秒同时冷启动门禁，不证明大于五实例、持续吞吐、
bit-exact BT controller、物理 PSRAM/cache timing、RF 或真机。

## 关键证据

- 两批 evidence 原始 SHA-256：
  `87dd71664fe4a9a7035051572a934254505608ce28313b7d5f0ff45fa857670a`
  和 `8f9a913af3af0b4c43326a363dec0d5766df10379f7bdd8f27d1bf6a48508e9f`。
- firmware SHA-256：
  `c3eaa35b9c41204cc6337e30b1d81f60bf06eab2d747f3547af5d8b8ba0ea99f`。
- 每 lease 固定 accelerator `tcg,thread=single,tb-size=128` 和
  `shift=5,align=off,sleep=off`。
- 每 lease HLI `45/45`、36 events/9 ACLs；errors/reset/panic/dropped 和
  队列深度均为 `0`。
- 源码提交 `39e6295`；GitHub Actions run `40193742174` 的
  `platform-contracts` 与 `network-namespace-policy` 均 PASS。

## 文件

- `report.md`：根因、改动、执行、验证和边界。
- `run.json`：结构化记录。
- `evidence/five-instance-fixed-icount-pass-a.json`：第一批原始 evidence。
- `evidence/five-instance-fixed-icount-pass-b.json`：第二批原始 evidence。
- `evidence/verification-summary.json`：提交、CI、测试和关键限制摘要。

## 未覆盖项

- 大于五实例、持续吞吐和 active-stop 之外的 teardown。
- bit-exact Espressif BT controller/baseband 与物理 RF。
- 物理 8 MiB PSRAM、cache timing、功耗和电气特性。
- 同固件 SHA 的真机路径。

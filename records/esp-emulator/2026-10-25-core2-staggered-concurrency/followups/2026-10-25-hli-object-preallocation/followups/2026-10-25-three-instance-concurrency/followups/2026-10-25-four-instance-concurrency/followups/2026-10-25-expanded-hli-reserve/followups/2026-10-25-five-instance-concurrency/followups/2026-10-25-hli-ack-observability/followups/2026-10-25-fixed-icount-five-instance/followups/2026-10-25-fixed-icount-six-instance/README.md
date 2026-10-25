# Core2 fixed-icount six-instance cold start

- 日期：`2026-10-25`
- 结果：`PASS`（仅 virtual-device validation）
- 工作类型：`code_change`
- 问题来源：Core2 fixed-icount 五实例门禁 follow-up
- 源码版本：`m5agent/m5stack-esp-emulator @ c72ac2f`
- 基线：`39e6295`
- 环境：macOS arm64、Python 3.13、Node.js、项目补丁 QEMU；未使用物理设备

## 结论

在固定 `icount shift=5,align=off,sleep=off`、BLE-first 测试 workload 和相同
firmware/ELF/QEMU 下，两批独立零错峰六实例 `6×120s` Device Service 门禁均为
`6/6 PASS`，合计 `12/12`，最大真实并发 6。

每个 lease 在同一 guest 内通过 WiFi DHCP/HTTP、公网 DNS/HTTP、外部 NUS
GATT、frame、31 节点 QOM、pcap、evidence 和 12–13 次 1 MiB PSRAM 全缓冲
读回；HLI `45/45`、36 events/9 ACLs，reset/panic/dropped 和队列深度为 0。
第二批一个 lease 记录一次可恢复 `hli-prealloc-failures=1`，随后仍完成全部
36/9 fast-path packet 和 45/45 HLI 投递；该瞬态作为诊断保留。

本结果关闭六实例 120 秒同时冷启动门禁，不证明大于六实例、持续吞吐、
bit-exact BT controller、物理 PSRAM/cache timing、RF 或真机。

## 关键证据

- 两批 evidence 原始 SHA-256：
  `ae49660be9ad1b67e8149bad46069e8c86e7c5892ca7148bac8828aca642751a`
  和 `6131b3c61a99bba93f45b50e34d0f114ea7142405cce4ef1352377ebf71d9b58`。
- firmware SHA-256：
  `c3eaa35b9c41204cc6337e30b1d81f60bf06eab2d747f3547af5d8b8ba0ea99f`。
- 每 lease 固定 accelerator `tcg,thread=single,tb-size=128` 和
  `shift=5,align=off,sleep=off`。
- 两批共 12 个 lease 完成 154 次 1 MiB PSRAM 全缓冲读回。
- 源码提交 `c72ac2f`；GitHub Actions run `40195028961` 的两个 job 均 PASS。

## 文件

- `report.md`：执行、证据、验证和边界。
- `run.json`：结构化记录。
- `evidence/six-instance-fixed-icount-pass-a.json`：第一批原始 evidence。
- `evidence/six-instance-fixed-icount-pass-b.json`：第二批原始 evidence。
- `evidence/verification-summary.json`：提交、CI、测试和关键限制摘要。

## 未覆盖项

- 大于六实例、持续吞吐和 active-stop 之外的 teardown。
- bit-exact Espressif BT controller/baseband 与物理 RF。
- 物理 8 MiB PSRAM、cache timing、功耗和电气特性。
- 同固件 SHA 的真机路径和本轮 clean source rebuild。

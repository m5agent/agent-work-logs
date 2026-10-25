# Core2 fixed-icount eight-instance cold start

- 日期：`2026-10-25`
- 结果：`PASS`（仅 virtual-device validation）
- 工作类型：`code_change`
- 问题来源：Core2 fixed-icount 六实例门禁 follow-up
- 源码版本：`m5agent/m5stack-esp-emulator @ a181ac9`
- 基线：`c72ac2f`
- 环境：macOS arm64、Python 3.13、Node.js、项目补丁 QEMU；未使用物理设备

## 结论

Device Service 当前每设备容量为 8。第一次八实例 `8×120s` control 使用旧
`hold/10` sweep 下限，结果为 `4/8`：四个失败 lease 均完成 11 次连续
1 MiB PSRAM 全缓冲读回，而所有八个 guest 的 HCI、WiFi、公网、NUS GATT、
frame、31 节点 QOM、pcap、evidence 均正常，reset/panic/dropped 为 0。
该 control 作为纯吞吐阈值失败保留。

将最高并发下的 sustained floor 校准为 `hold/12` 后，两批独立零错峰
`8×120s` 均为 `8/8 PASS`，合计 `16/16`，达到当前服务单设备容量上限。
每 lease 完成 11–12 次 PSRAM 全缓冲读回，两批各保留一次可恢复
`hli-prealloc-failures=1` transient。

本结果关闭当前配置下八实例 120 秒同时冷启动门禁，不证明大于八实例、
持续吞吐、bit-exact BT controller、物理 PSRAM/cache timing、RF 或真机。

## 关键证据

- threshold-fail SHA-256：
  `a1241057e0063de5cdf16564dc1c986291469ea60ff4f17461e3d55d488b2a0a`。
- pass A/B SHA-256：
  `36d52c32d6156b6282c1208a72f12eac50b1d87eacbb85cc9caf2a47ce1f989c`
  与 `96d12ff41e2def7ab48813b499590a914de6b6da3ed7805b69c1f26d7d971fe7`。
- firmware SHA-256：
  `c3eaa35b9c41204cc6337e30b1d81f60bf06eab2d747f3547af5d8b8ba0ea99f`。
- 每 lease 固定 `tcg,thread=single,tb-size=128` 和
  `shift=5,align=off,sleep=off`。
- 两批共 16 个 PASS lease，完成 188 次 1 MiB PSRAM 全缓冲读回。
- 源码提交 `a181ac9`；GitHub Actions run `40196580736` 的两个 job 均 PASS。

## 文件

- `report.md`：control、校准、复跑和验证边界。
- `run.json`：结构化记录。
- `evidence/eight-instance-threshold-fail.json`：旧 floor 的校准 control。
- `evidence/eight-instance-fixed-icount-pass-a.json`：确认批 A。
- `evidence/eight-instance-fixed-icount-pass-b.json`：确认批 B。
- `evidence/verification-summary.json`：提交、CI、测试和限制摘要。

## 未覆盖项

- 大于服务当前容量 8 的实例数。
- 持续吞吐和 active-stop 之外的 teardown。
- bit-exact Espressif BT controller/baseband 与物理 RF。
- 物理 8 MiB PSRAM、cache timing、功耗和电气特性。
- 本轮 clean source rebuild 和同固件 SHA 真机验证。

# ESP Emulator current work reconciliation and Core2 121-cycle reconnect

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device + docs/contract）
- 工作类型：`code_change`
- 问题来源：旧文档混合了已完成、在途和已推翻的结论；Core2 121 轮门禁需要重跑
- 源码版本：`m5agent/m5stack-esp-emulator @ d9008a3c94582281cbedf079a95be2b5f02f74d5`
- 环境：macOS Apple Silicon；补丁 QEMU；Device Service `/api/v1`；Bumble peer

## 结论

项目文档已按职责重新收敛：README 只保留入口和摘要，
`project-status.md` 维护当前能力，`project-backlog.md` 维护未完成 Task，
`validation-ledger.md` 维护带日期的证据，`code-map.md` 维护代码和测试入口。
过期结论已移除，包括“最终两小时复测未完成”、固定 readiness 预算、以及
服务重启时所有活动 session 一律 failed 等旧描述。

代码侧修复了两个独立的 max-duration reconnect harness 缺陷：

1. Device Service 和 runner 现在共享按 cycles/delay 计算的 readiness 预算；
   `121` 轮、`2s` delay 的 effective timeout 为 `1028s`。
2. reconnect-only 路径没有 hold loop，原先不会采样 QEMU accelerator；runner
   现在于 session 首次进入 running 时直接采样 live QEMU command。

修复后，单个 artifact-bound Core2 lease 完成 `121/121`：

- `tcg,thread=single,tb-size=128`、WiFi/公网、NUS GATT、frame/QOM、pcap、
  evidence 和 cleanup 全部 PASS；
- HLI `3405/3405`、events 2316、ACLs 1089；
- errors、HLI/meta/TX queue、dropped、last-error、peer-close 和 panic 均为 0；
- firmware/ELF/QEMU 和 runner/service/accelerator/BLE-limit 工具哈希无漂移。

## 关键证据

- 平台套件：`355/355 PASS`；文档契约 `19/19`；Node `2/2`.
- CI：`40119682055`、`40120748391`、`40121973524` 全部成功。
- 单 lease 121 轮：`evidence/verification-summary.json`。
- 源码证据：
  [reconnect121-1x](https://github.com/m5agent/m5stack-esp-emulator/blob/d9008a3c94582281cbedf079a95be2b5f02f74d5/tests/uiflow2/core2_native_hci/evidence-2026-10-25-hci4-reconnect121-1x.json)

## 文件

- `report.md`：根因、代码改动、执行与边界
- `run.json`：结构化结论
- `evidence/verification-summary.json`：脱敏验证摘要

## 未覆盖项

- 另外两个独立 lease 的 121 轮复现，因此 `3/3` 门禁仍为 `NOT RUN`；
- bit-exact ESP32 BT controller/baseband；
- 物理 cache/PSRAM、RF、功耗和真机验证。

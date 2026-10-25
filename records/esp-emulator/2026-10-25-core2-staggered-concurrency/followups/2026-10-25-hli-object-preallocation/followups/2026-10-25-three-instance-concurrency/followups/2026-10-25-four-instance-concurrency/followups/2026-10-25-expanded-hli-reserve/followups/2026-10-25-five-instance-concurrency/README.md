# ESP Emulator Core2 five-instance staggered concurrency

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation；仅限 30 秒错峰稳态）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`b8b48e46c79d65f151eca1a57431c3117fb95907`
- 结果版本：`8c4349cd09a0c2cfd7362830df1825d76615ac9b`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40183597823>
- CI 结果：`PASS`（`platform-contracts`、`network-namespace-policy`）
- 环境：macOS Apple Silicon；Python 3.13；Node 20；QEMU virtual device；
  无物理硬件

## 结论

父记录关闭了四实例零错峰边界。本 follow-up 把 runner 的并发上限从固定
`4` 改为与 Device Service 单设备容量一致，并在该版本上验证五实例。

两批独立 `5×120s`、30 秒 startup stagger 均为 `5/5 PASS`，合计
`10/10 PASS`，实际最大并发为 `5`。每个通过 lease 都在同一实例内完成
WiFi、公网 DNS/HTTP、外部 BLE NUS GATT、持续 PSRAM stress、
frame/31-node QOM、pcap、evidence 和 cleanup；HLI `45/45`、
36 events/9 ACLs、reserve depth `8/4`，errors/reset/panic 均为 `0`。

零错峰五实例仍为 `OPEN / UNSTABLE`。相同 firmware/ELF/QEMU/tool
hashes 下，一批 `5/5 PASS`，独立确认批却为 `3/5 FAIL`；失败分别出现
`LoadProhibited @ 0x402630cc`、HLI queue 残留和 external GATT exchange
failure。因此 `10/10` 错峰稳态不能继承给同时冷启动，更多实例也仍为
`NOT RUN`。

## 关键证据

- firmware SHA-256：
  `5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
- ELF SHA-256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
- 错峰 QEMU SHA-256：
  `6f505d4a5755254490beb8fc10131d4a9e0357db34c621c698ede05db48f25b1`；
- 零错峰 QEMU SHA-256：
  `0e1165fb866ecb573cdaca2084bdf498b45432aaa1937674ca73d04eeaa7a7fc`；
- runner SHA-256：
  `78385772a35aef27c3560f40cc47b44d34cbdedfc6864dbdb2078a20066d8f3a`；
- 两批错峰 aggregate：`5/5 PASS`、`5/5 PASS`，合计 `10/10`；
- 零错峰对照：`5/5 PASS` 一批，独立确认批 `3/5 FAIL`；
- 平台契约：`470/470`；文档契约：`37/37`；Node units：`2/2`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  compileall、Ruff `E9/F` 和 `git diff --check`：`PASS`。

## 文件

- `report.md`：执行、失败对照、验证层级和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏聚合摘要；
- `evidence/evidence-2026-10-25-core2-concurrent-5x120-stagger30-pass-a.json`：
  错峰首批；
- `evidence/evidence-2026-10-25-core2-concurrent-5x120-stagger30-confirm-pass-b.json`：
  错峰独立确认批；
- `evidence/evidence-2026-10-25-core2-concurrent-5x120-no-stagger-pass-1.json`：
  零错峰通过对照；
- `evidence/evidence-2026-10-25-core2-concurrent-5x120-no-stagger-fail-1.json`：
  零错峰独立失败对照。

## 未覆盖项

- 零错峰五实例冷启动稳定性；
- 大于五实例的并发；
- 长时吞吐和 active-stop 之外的其他 teardown；
- bit-exact Espressif BT controller/baseband；
- 物理 PSRAM/cache timing、RF、功耗和电气；
- physical hardware validation。

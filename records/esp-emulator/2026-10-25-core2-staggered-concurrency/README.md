# ESP Emulator Core2 staggered concurrent unified leases

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`a358780eb572a9642bdf5f180572ef689529cf9c`
- 结果版本：`e3c5d089c33397c1948fb611e776d75cb3c20bd8`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40168564543>
- 环境：macOS Apple Silicon；Python 3；Node 20；QEMU `80d3c50d…`；
  Core2 unified 16 MiB firmware；无物理硬件

## 结论

Core2 `qemu-unified/core2-native-hci` 首次完成两个 artifact-bound lease 的
并发稳态门禁：

- 两个 lease 使用同一 firmware/ELF/QEMU，启动错峰 `30s`；
- 最大并发 session 数为 `2`；
- 两个 lease 各保持 `120s`，运行区间真实重叠；
- 每轮独立完成 WiFi DHCP/HTTP、公网 DNS/HTTP、external NUS GATT、
  active BLE、30+ 次 `1 MiB` PSRAM sweep、frame/QOM、pcap、
  bounded TCG、evidence 和 cleanup；
- 最终 `2/2 PASS`，frame/QOM 一致，HLI `45/45`，无 panic。

过程中先复现并保留了两个失败：

1. 两个 session 共享宿主 HTTP `18089` 时，第二个 session 得到
   `Address already in use`；
2. 改用 per-session QEMU `guestfwd` 后，无启动错峰的同时冷启动仍使第二个
   guest 在 `ble_hs_hci_process_ack` (`0x402630cc`) 触发
   `LoadProhibited`。

因此本记录只关闭“30 秒错峰后的并发稳态”部分。无错峰同时冷启动、持续
吞吐、bit-exact BT controller/baseband、物理 cache/PSRAM 和真机仍开放。

## 关键证据

- 平台测试：`460/460 PASS`；
- 文档契约：`35/35 PASS`；
- Node SHA256/upload：`2/2 PASS`；
- Core2 concurrent fixture：`19/19` 聚合检查项 `PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、project snapshot、
  Ruff `E9/F`、compileall、`git diff --check`：`PASS`；
- CI `platform-contracts` 与 `network-namespace-policy`：`PASS`。

## 文件

- `report.md`：失败复现、guestfwd 修复、错峰并发验证和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：脱敏验证摘要；
- `evidence/core2-concurrent-2x120-stagger30.json`：最终 PASS；
- `evidence/core2-concurrency-http-port-collision-fail.json`：共享端口失败；
- `evidence/core2-concurrency-simultaneous-start-fail.json`：无错峰冷启动失败。

## 未覆盖项

- 无错峰同时冷启动；
- 2 个以上 lease、长时间吞吐和更多 teardown 模式；
- bit-exact Espressif BT controller/baseband；
- 物理 PSRAM/cache timing、RF、功耗和电气；
- physical hardware validation。

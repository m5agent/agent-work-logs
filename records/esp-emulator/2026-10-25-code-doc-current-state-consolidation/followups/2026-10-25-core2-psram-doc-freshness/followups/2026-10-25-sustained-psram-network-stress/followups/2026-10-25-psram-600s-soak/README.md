# ESP Emulator Core2 600-second PSRAM soak

- 日期：`2026-10-25`
- 结果：`PASS`（virtual-device；物理硬件 `NOT RUN`）
- 工作类型：`code_change`
- 源码仓库：<https://github.com/m5agent/m5stack-esp-emulator>
- 基线版本：`2a3e8120c5548110fad032d0172a3f7dd7a15e13`
- 结果版本：`a9d60e12599b10ea2602b00e88dbf7742c800868`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40150913419>
- 环境：macOS Apple Silicon；真实 Device Service `/api/v1`；QEMU

## 结论

同一 Core2 `core2-native-hci` 镜像在单 lease 600 秒内保持：

- 179 次 1 MiB PSRAM 全缓冲校验，约 179 MiB；
- 51 次受控 HTTP recheck；
- 18 次公网 DNS/HTTP recheck；
- active BLE 与外部 NUS GATT；
- bounded TCG、frame、34 节点 QOM、pcap、evidence 和 cleanup。

HLI 为 `45/45`，errors、queue、dropped、peer-close 和 panic 均为 0。pcap 为
97,951 B、912 packets、208 flows，包含 DHCP DORA 和 `example.com` DNS。
20 个 host RSS 采样从 327472 到 327824 KiB（+352 KiB），phys footprint
从 246784 到 187392 KiB；该结果只覆盖当前虚拟 workload。

## 关键证据

- 结果：`1/1 PASS`；
- firmware SHA256：`5ed4fcfad22c50d10d9a1af48bdb8e7b7e125a6fa278d3f8e30e53bd03aa43db`；
- 输入与工具哈希：运行期无漂移；
- frame：3,731 B，SHA256 `cd2f2033…`；
- pcap：912 packets、208 flows；
- 与 `3×120s` 使用相同 firmware/runner/QEMU 哈希。

## 文件

- `report.md`：执行、结果和边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

## 未覆盖项

- 物理板载 8 MiB PSRAM 和物理 cache/PSRAM timing；
- bit-exact Espressif BT controller/baseband；
- 两小时 soak 与持续 PSRAM 校验的组合；
- 长时并发/吞吐、其他 teardown、RF、功耗和真机。

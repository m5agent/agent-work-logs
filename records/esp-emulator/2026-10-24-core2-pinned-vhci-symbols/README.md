# ESP Emulator Core2 native-VHCI ELF 固定符号与文档对账

- 日期：`2026-10-24`
- 结果：`PASS`（虚拟设备、代码与文档范围）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`829d64e99ae318c6d78de0729bb6a75f8455373c`
- 结果版本：`455504dab038975a3deb601d48c3c3604fff5a1d`
- 环境：macOS Apple Silicon；现有 Xtensa QEMU、Core2 参考固件、Bumble peer

## 结论

Core2 stock native-VHCI 路径不再通过 GDB `parse_and_eval` 查询符号。
Device Service 和独立 runner 都从匹配 ELF 严格解析
`API_vhci_host_send_packet`、`vhci_env_p`、`esp_cpu_wait_for_intr`，再以
固定地址启动 bridge。

真实 ELF 解析值与 GDB 对照一致。pinned-symbol standalone 外部 NUS GATT
为 `5/5`，同 guest board+WiFi+公网+native-VHCI BLE 为 `3/3`；整理后的
工作树又完成一次 standalone `1/1`。平台测试为 `243/243`，GitHub Actions
`platform-contracts` 与 `network-namespace-policy` 均 PASS。

这次只移除了“符号查询”对 GDB 的依赖。GDB 仍负责 guest 暂停、breakpoint/
callback 注入和 synthetic send-frame return，因此不能把结果写成无调试器或
bit-exact ESP32 BT controller。

## 关键证据

- ELF 固定地址：`0x403064d8`、`0x3ffcc0a4`、`0x40093578`；
- standalone pinned-symbol：`5/5 PASS`；
- unified pinned-symbol：`3/3 PASS`；
- GitHub Actions：`40003866186` 两个 job PASS；
- Device Service `core2-native-vhci`：已有带 symbol event 的单 lease PASS；
- 重复 Device Service lease 稳定门禁：尚未建立；
- 物理硬件、RF、coexistence 与 soak：`NOT RUN`。

## 文件

- `report.md`：实现、验证、失败实验和边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合证据。
- `followups/2026-10-24-service-repeat-stability/`：后续同 commit
  Device Service repeated lease 为 `1/2`；BLE C2H callback 注入失败，
  WiFi/公网仍 PASS。

## 未覆盖项

- GDB 暂停、callback 注入和 synthetic return 的移除；
- 同 commit 固定次数重复 Device Service lease；
- bit-exact Espressif classic ESP32 BT controller/baseband；
- 物理 cache/PSRAM 等价性、RF、coexistence、throughput 和 soak；
- 真机同路径验证。

# Core2 native HCI Device Service five-lease gate

- 日期：`2026-10-24`
- 结果：`PASS`（virtual-device validation）
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`30022795b2ac0956d9bc2b3225398d406a17a27f`
- 结果版本：`de5a6c737548c88ade1e318d424da254e3d0778c`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40054836265>
- 环境：macOS Apple Silicon；QEMU 9.2.2 Xtensa；`m5core2`；
  stock UIFlow2 v2.5.3 build

## 结论

`CORE2-01` 的 `HCI-4` 已闭环。规范 profile
`qemu-unified/profile=core2-native-hci` 通过五个独立 Device Service
`/api/v1` lease。每个 lease 都同时验证：

- 320×240 frame；
- 27 节点 QOM；
- WiFi DHCP 和受控 HTTP；
- 公网 IPv4 DNS/HTTP；
- Bumble 外部 NUS discovery/subscription/write/notify；
- pcap 和 session-bound evidence ZIP。

五个 lease 的 `gdb_bridge=false`，frame SHA256 均为
`5bfcdf8fc518a36385783a9b5bf09b3fbce9d8c07406326955569f6c7db8408b`。
完成文档对账后，更新后的 runner 又在临时服务中重新实跑 `1/1 PASS`。

旧 `core2-native-vhci` 的 repeated lease 只有 `1/2`，现明确保留为
GDB 诊断/兼容路径；新调用以 `core2-native-hci` 为准。

## 关键证据

- 固件 SHA256：
  `65c27baf132db1e8d97207d812dd945c782adcfb5ffc1ec67a4eee5656782e5d`
- ELF SHA256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`
- QEMU SHA256：
  `29b30d78d8634aad22877f3f893d8f35a8b10870c8b4870e26c7eaf3cfc4ccdf`
- Device Service `5/5 PASS`，`gdb_bridge=false`；
- 本地平台套件 `283/283 PASS`；
- GitHub Actions `283` tests、`OK (skipped=2)`，两个 job 均 PASS；
- Node SHA256/upload tests `2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles 和 OpenAPI YAML PASS。

## 文件

- `report.md`：实现、文档对账、验证与剩余边界；
- `run.json`：结构化记录；
- `evidence/verification.summary.json`：脱敏聚合证据。

源仓库证据：
<https://github.com/m5agent/m5stack-esp-emulator/blob/de5a6c737548c88ade1e318d424da254e3d0778c/tests/uiflow2/core2_native_hci/evidence-2026-10-24-hci4-service-5x.json>

## 未覆盖项

- bit-exact Espressif BT controller/baseband；
- 物理 cache/PSRAM 时序等价性；
- RF、coexistence、throughput 和长期 soak；
- 物理硬件验证；
- 恶意固件沙箱；
- 其他 Core2 固件 build。当前 hook 偏移绑定已验证的 UIFlow2 v2.5.3
  build，不能仅凭 SoC 和符号名复用该 PASS。

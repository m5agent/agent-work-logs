# Core2 native-VHCI Device Service 重复 lease 稳定性

- 日期：`2026-10-24`
- 结果：`FAIL`（重复 lease 验收）
- 工作类型：`service_debug`
- 源码版本：`455504dab038975a3deb601d48c3c3604fff5a1d`
- 证据版本：`f4e1b43809be714f53387ec01ce6639b468e3eb6`
- 环境：macOS Apple Silicon；双 CPU `m5core2`；deterministic TCG/icount；
  Device Service `/api/v1`；QEMU VHCI→Bumble

## 结论

同一固件、ELF 和 `core2-native-vhci` profile 连续执行两次独立 Device
Service lease，结果为 `1 PASS / 1 FAIL`，不能把此前单 lease PASS 当作稳定。

失败 lease 的 WiFi、DHCP、controlled HTTP、公网 DNS/HTTP 仍 PASS；BLE
在初始化阶段失败。Bumble 返回 `LE Set Event Mask` 的 Command Complete 后，
GDB bridge 从 H2C sender context 调用 firmware host callback 返回
`2559356`，随后 GDB 报 target-running，guest 抛出
`InstrFetchProhibited` 并重启。

结果提交的 GitHub Actions `40009284990` 中 `platform-contracts` 和
`network-namespace-policy` 均 PASS；CI 通过不代表 repeated lease 门禁通过。

## 文件

- `run.json`：结构化结果与失败分类；
- `evidence/summary.json`：脱敏的两次 lease checks 和哈希。

## 未覆盖项

- GDB callback/return 控制面的修复；
- 更长时间重复 lease、长稳和真机验证；
- bit-exact Espressif BT controller/baseband。

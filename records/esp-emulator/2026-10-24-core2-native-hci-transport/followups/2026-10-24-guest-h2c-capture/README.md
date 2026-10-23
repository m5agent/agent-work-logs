# Core2 guest H2C capture without GDB

- 日期：`2026-10-24`
- 结果：`PARTIAL`（首个 guest H2C 捕获 PASS；完整 sequence 未执行）
- 工作类型：`code_change`
- 源码版本：`7f8343d0b3c5e0ecfac90d24084e250c0ad5a5f9`
- 环境：macOS Apple Silicon；QEMU 9.2.2 Xtensa；stock Core2 UIFlow2 镜像

## 结论

QEMU `esp32-native-hci` 通过 ELF-known `vhci_env_p`、VHCI buffer/length
字段捕获 guest H2C，不再依赖 GDB：

```text
peer H4 packet    01030c00
decoded           HCI Reset
QOM h2c-packets   1
QOM h2c-bytes     4
QEMU exit         0
```

GitHub Actions `40010980506` 的 `platform-contracts` 和
`network-namespace-policy` 均 PASS。

这是 guest→QEMU 的首个真实 packet，不等于完整 H2C sequence 或 BLE PASS。
guest 要收到 C2H 才能继续发送 LE init 和 advertising 命令。

## 文件

- `run.json`：结构化结果；
- `evidence/summary.json`：脱敏的开源证据摘要。

## 未覆盖项

- QEMU→guest C2H delivery；
- 完整 Reset/LE init/advertising sequence；
- BLE discovery/GATT；
- repeated Device Service lease；
- bit-exact controller/baseband 与物理硬件。

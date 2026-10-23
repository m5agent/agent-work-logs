# ESP Emulator Core2 native-VHCI Device Service

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`bf500ec3a6287586bdb28713a0feedc7e19a9eaf`
- 基线版本：`7823befc2cee622e6b086287f5ae903fda839885`
- 环境：macOS Apple Silicon；本地 Device Service；QEMU `m5core2`；Bumble

## 结论

新增正式 `runtime=qemu-unified`、`profile=core2-native-vhci` 路径。通过真实
`/api/v1` 上传固件和匹配 ELF、创建 lease 后，同一个 QEMU guest 完成：

- 320x240 board/display/touch；
- ACPI/QOM 电源、IMU、RTC 读取；
- speaker/microphone PCM；
- WiFi/DHCP 和受控 HTTP；
- 公网 IPv4 DNS/HTTP；
- stock ESP32 VHCI → Bumble 外部 NUS GATT；
- frame、QOM、pcap、bridge 和 peer evidence。

network evidence 的 18 项检查全部 PASS。

## 关键结果

- API runtime：`qemu-unified`
- profile：`core2-native-vhci`
- firmware SHA256：
  `f19597358e93279e8996f469aadf6e4a828c5e5285ef2f31212290c3df597ba2`
- matching ELF SHA256：
  `5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`
- evidence ZIP SHA256：
  `ddcf4e23b03587aeb4e791089474b8f0cadce0d2c9db06ce4f2e52d8757a7857`
- pcap：54 packets，summary PASS；
- platform tests：`213/213 PASS`；
- physical hardware：`NOT RUN`。

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- `core2-native-vhci` 仍依赖 GDB 诊断桥，不是无调试器的 QEMU 内部后端；
- bit-exact Espressif BT baseband/controller 未执行；
- RF、coexistence、配对/安全、吞吐、功耗和真机验证未执行。

# ESP Emulator DHCP Lease Renewal

- 日期：`2026-10-24`
- 结果：`PASS`
- 工作类型：`code_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`71ab6ef95094b9bfe89ab364035c940f9e14c893`
- 基线版本：`e14169f4c49d8651444b987172b0ab0135a93e11`
- 环境：macOS Apple Silicon；ESP-IDF 5.5.4；ESP32-S3 QEMU

## 结论

新增 ESP-IDF DHCP renewal probe，并通过真实 Device Service
`qemu-wifi/profile=uiflow2-sticks3-wifi` lease 验证：

- guest 获得初次 DHCP lease；
- guest 调用 `netifapi_dhcp_renew()`；
- QEMU pcap 看到初次 `DISCOVER/OFFER/REQUEST/ACK`；
- 同一 transaction 随后出现 renewal `REQUEST/ACK`；
- `renewal_requests=1`、`renewal_acks=1`；
- lease 为 `86400s`，地址保持 `10.0.2.15`；
- renewal 后 controlled HTTP 返回 200；
- session 停止后保留串口、pcap 和 network evidence。

## 关键结果

- 平台测试：`235/235 PASS`；
- FirmwareManifest `flasher-args` round-trip：`PASS`；
- firmware image SHA256：
  `5d990abc6d6b81c71b5e7d243f06171d8c6dd6c09c269e94549f51954957de46`；
- pcap DHCP message types：
  `discover=1, offer=1, request=2, ack=2`；
- API runtime contract：`1.11.0`；
- 物理硬件：`NOT RUN`。

## 文件

- `report.md`
- `run.json`
- `evidence/verification.summary.json`

## 未覆盖项

- 真实虚拟 AP/radio 消失和恢复；
- 不同 lease/address 重新分配；
- WPA2/WPA3、RF、物理链路和真机；
- 双设备 lab fabric。

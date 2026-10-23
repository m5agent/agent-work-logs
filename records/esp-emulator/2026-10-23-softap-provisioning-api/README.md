# ESP Emulator firmware SoftAP 配网 API

- 日期：`2026-10-23`
- 结果：`PARTIAL`
- 工作类型：`code_change`
- 问题来源：用户询问固件创建 WiFi 热点并由手机配网的审查路径
- 源码版本：[`m5stack-esp-emulator@6bcd6e8`](https://github.com/m5agent/m5stack-esp-emulator/commit/6bcd6e88c485ec89fe70e8fa35d91282230929a0)
- 环境：macOS；ESP-IDF 5.5.4；`esp-emu` 0.50.0；Device Service API `1.5.0`

## 结论

Device Service 已补充固件 SoftAP 审查入口：`firmware_ap_password` 让模拟器作为
station 加入固件热点，`hostfwd` 将配网端口限制在 reviewer loopback。虚拟
ESP32-S3 设备成功加入官方 ESP-IDF captive portal 固件创建的热点、取得 DHCP
lease、访问配网根页面并记录 `HTTP 200`。手动停止 session 时也会先收尾
`evidence.json`，不再丢失运行证据。

这项结论覆盖 API 契约、虚拟烧录、WiFi 关联、DHCP、配网页 GET 和生命周期证据。
完整手机配网尚未闭环：表单 POST、凭据写入 NVS、AP 到 STA 的切换和重启后持久化
均为 `PARTIAL` 或 `NOT RUN`。

## 关键证据

- 回归：`176` 个 platform tests 通过；runtime coverage 与 peripheral catalog 检查通过。
- 构建：ESP-IDF 5.5.4 captive portal，目标 ESP32-S3。
- 镜像：merge SHA256 `0fb48462902ec70a886ae0db8d06bf08b35e3ca5646fc9d690f54e3d890d66c9`，
  8 MiB Device Service flash SHA256
  `35f383ffd03718c7a42e3faccdf9d97491d9286239d3b3cc462be327bf79ee9d`。
- 协议：SoftAP 启动、虚拟 station 关联、DHCP lease、HTTP `Serve root` 均在串口出现。
- HTTP：配网根页面返回 `200`，259 bytes，响应 SHA256
  `020854836e150511586bb17849dff5783d369c7f574260f20e93284a3d7c51f8`。
- 停止：`stop_requested=true`、`timed_out=false`，session 保持 `stopped`，
  network evidence 为 `PARTIAL`。
- 脱敏：持久化 session 中 WiFi 与 firmware AP 凭据均为 `<redacted>`。

## 文件

- `report.md`：实现、验证步骤、边界与风险
- `run.json`：结构化结果
- `evidence/`：测试、协议、HTTP 和 API 摘要
- `patches/`：不适用；完整可审阅改动使用源码 commit 固定链接
- `code/`：不适用；复现工程来自公开 ESP-IDF captive portal 示例

## 未覆盖项

- 实际手机 OS 的 captive portal 探测、证书和浏览器差异；
- 配网表单 POST、错误输入、凭据写入 NVS；
- 配网后自动切换 STA、访问受控公网端点、重启后凭据保留；
- WPA3-SAE-only、隐藏 SSID 和其它热点安全模式；
- 同一 guest 内配网页和 StickS3 framebuffer/input 的联合验证；
- 物理硬件、RF、功耗与性能验证。

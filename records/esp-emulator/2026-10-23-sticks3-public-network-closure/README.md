# StickS3 public network closure and NTP diagnosis

- 日期：`2026-10-23`
- 结果：`PASS`
- 工作类型：`code_change`
- 问题来源：用户询问 StickS3 虚拟设备网络为何仍显示未闭环
- 源码版本：`m5stack-esp-emulator @ 5ab6251c18f06e7414701c494d406ed6071b2d33`
- 环境：QEMU StickS3、Device Service `qemu-wifi`、QEMU user networking
- 验证类别：`virtual-device validation`

## 结论

StickS3 的公网 HTTP 数据面已经闭环：设备侧完成 Wi-Fi/DHCP、DNS、公网 TCP、
HTTP 200 和实时 JSON 解析，宿主侧同一 API 返回的温度、湿度、天气码与设备侧
一致。`/network` 原先显示 `PARTIAL` 是因为调用方没有提供
`expected_markers`，不是网络失败；补齐设备 marker 后状态为 `PASS`。

随后定位并修复了第二个状态展示问题：live snapshot 与 stop 原先可能继续
保留启动时的空串口 `PARTIAL`，即使 `/network` 已实时返回 `PASS`。修复后
stop 会在终止 guest 前重新采样，停止响应和 `session.json` 均保留最终 `PASS`。

CYBER CLOCK 的 `NTP failed` 是应用层超时与服务器选择问题：它先访问当前环境
超时的 `ntp.aliyun.com` 和 `ntp.tencent.com`，只等待 5 秒；LWIP SNTP 默认
单服务器接收超时是 15 秒，因此还没切换到可用的 `pool.ntp.org` 就关闭了
Wi-Fi。UIFlow 日志中的 `transport_ws` 是设备到 `uiflow2.m5stack.com` 的
控制面 WebSocket 被服务端关闭，不阻断同一会话的业务 HTTP。

## 关键证据

- Device Service 网络检查：5/5 marker PASS。
- 停止后的 session snapshot 与持久化 `session.json`：仍然 5/5 marker PASS。
- 设备：DNS 成功、公网 HTTP 200、Shenzhen `31.0 C / 39% / code 0`。
- 宿主：同一 Open-Meteo API 返回 `30.8 C / 39% / code 0`。
- 宿主 NTP：阿里云和腾讯超时，`pool.ntp.org` 返回 48 字节响应。
- CYBER CLOCK 源码：3 台服务器、`20 x 250 ms = 5 s` 总等待窗口。

## 文件

- `report.md`：完整链路、根因和修复建议
- `run.json`：结构化证据
- `evidence/summary.md`：脱敏后的分层结果
- `evidence/sticks3-weather.png`：设备侧实时天气画面
- `evidence/cyber-clock-timezone.png`：NTP 失败后的时区画面

## 未覆盖项

- 未修改或重新发布第三方 CYBER CLOCK 固件。
- 未执行真实 StickS3 射频、功耗或电气测量。
- 未把 UIFlow 控制面 WebSocket 故障冒充为公网 HTTP 故障。

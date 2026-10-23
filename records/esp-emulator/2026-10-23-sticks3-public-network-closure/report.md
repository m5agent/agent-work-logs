# StickS3 public network closure report

## 背景

StickS3 会话已经能显示应用和处理按键，但 Device Service 的 `/network`
仍返回 `PARTIAL`。用户要求确认虚拟设备是否能真正访问公网，并解释为什么
CYBER CLOCK v1.1.2 会显示 `NTP failed`。

## 结论

### 公网 HTTP：PASS

天气应用运行在 StickS3 QEMU 实例中，使用 QEMU user networking。设备侧串口
依次输出 Wi-Fi 连接、DNS 解析、HTTP 200、天气 JSON 解析和 READY marker。
宿主侧在同一时间窗口请求同一 Open-Meteo 端点，返回相同的温度、湿度和天气码。

### Device Service 状态：PARTIAL 的根因是缺少 marker

`qemu-wifi` 状态机只有在调用方提供 `expected_markers` 且全部匹配时才返回
`PASS`。原始会话没有配置 marker，因此即使串口已有完整业务证据，仍返回
`PARTIAL`。重新创建会话并提供五条 marker 后，`/network` 返回：

```text
status=PASS
marker:1=true
marker:2=true
marker:3=true
marker:4=true
marker:5=true
```

### CYBER CLOCK NTP：应用等待窗口过短

CYBER CLOCK 的代码顺序为：

```text
configTime(..., "ntp.aliyun.com", "ntp.tencent.com", "pool.ntp.org")
20 retries * 250 ms = 5 seconds
```

当前网络环境中 `ntp.aliyun.com` 和 `ntp.tencent.com` 的 UDP/123 请求超时；
`pool.ntp.org` 可返回有效 SNTP 响应。ESP-IDF LWIP 默认
`SNTP_RECV_TIMEOUT=15000 ms`，所以第一个不可达服务器会阻塞服务器切换窗口。
应用在 5 秒后退出并关闭 Wi-Fi，早于 SNTP 的下一次切换。

修复建议：

1. 将 `pool.ntp.org` 放第一优先；或
2. 把应用轮询窗口提高到 20-30 秒；或
3. 使用当前网络可达的 NTP 服务并保留远端备用地址。

### WebSocket 错误：控制面，不是业务数据面

UIFlow2 固件内置 webrepl 客户端会连接：

```text
ws://uiflow2.m5stack.com/ws/realtime?role=device&mac=...
```

服务端关闭连接后产生 `ESP_ERR_ESP_TLS_TCP_CLOSED_FIN`。同一会话中的
Open-Meteo DNS、TCP 和 HTTP 请求仍然成功，因此该日志不能解释天气数据失败，
也不应被当作设备无法上公网的证据。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| Wi-Fi | PASS | 扫描、认证、关联和 DHCP |
| DNS | PASS | 设备解析 Open-Meteo 到公网映射地址 |
| 公网 TCP | PASS | HTTP 连接完成 |
| 业务 HTTP | PASS | 状态 200，实时 JSON 可解析 |
| 实时数据 | PASS | 与宿主同端点结果一致 |
| Device Service 闭环 | PASS | 5 个 expected markers 全部匹配 |
| CYBER CLOCK NTP | FAIL | 应用 5 秒等待短于 SNTP 15 秒接收超时 |
| 物理硬件 | NOT RUN | 本轮为 virtual-device validation |

## 风险与回滚

本轮没有修改第三方固件。修改验证 policy 和源码提交可以独立回滚；不会影响
已保存的 Device Service 会话历史。

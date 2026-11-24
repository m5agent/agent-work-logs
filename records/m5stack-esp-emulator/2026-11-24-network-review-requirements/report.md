# 完整报告：模拟器网络审查能力需求

## 1. 数据与根因

审查服务窗口（2026-11-23 00:00 至 2026-11-24 11:53 +08:00）共 27 条任务：

- `done/SIM_VERIFIED` 6
- `manual_review` 21
- `failed` 0

人工复核中 **11 条**是 `E_NETWORK_PARTIAL`（52%）：

| 原因 | 数量 |
| --- | --- |
| `worker_namespace_unavailable` | 7 |
| `board_not_advertised` | 3 |
| qemu-wifi `PARTIAL`（需 hold B 启动 web server） | 1 |

审查服务的新版网络路径要求：

```text
native_sta_worker_ready(worker) =
  worker.accepting_leases
  and not worker.stale
  and worker.capabilities.qemu
  and worker.capabilities.pcap
  and worker.capabilities.network_namespace_platform == "linux"
  and worker.capabilities.network_namespace == "probe-on-admission"
```

本机 Device Service 在 macOS；配置的 Linux worker 只准入
`cardputer_adv_pronunciation` 和 `core2_2048`。因此通用固件的 Wi-Fi 声明无法进入
同 guest 数据面，只能 `NOT RUN` → 人工。

但设备目录显示 Cardputer / Cardputer-ADV 已有：

```json
"native_network": {
  "sta": {
    "runtime": "qemu-wifi",
    "profile": "generic-observe",
    "operation_assertions": false,
    "http_post_fixture": true,
    "tcp_fixture": true
  }
}
```

说明模拟器侧并非完全没有模型；缺的是**可移植、审查可判定的网络后端**，以及
**setup input / events / 断言**。

## 2. 需求

### P0：portable review-sta

- `runtime=qemu-wifi`，同 guest，保留 frame/serial/input/pcap；
- 不依赖宿主 Linux namespace/root/nftables/iproute2；
- 虚拟 AP + 固定 fixtures；默认无宿主 egress；
- 每会话隔离；支持 open 与 WPA2-PSK；错误密码必须 FAIL，不能 PARTIAL；
- capability 明确 `network_isolation=userspace-fixture-only`、`host_egress=deny`，
  并可提供 pcap 证明没有 fixture 之外的流量。

### P0：fixtures + setup inputs + events

建议会话请求：

```json
"network": {
  "profile": "review-sta",
  "ssid": "M5-REVIEW",
  "password": "<fixture-password>",
  "security": "wpa2-psk",
  "fixtures": {
    "dhcp": true,
    "dns": {"A": {"example.test": "192.0.2.2"}},
    "http": {"routes": [{"method":"GET","path":"/api/status","status":200,"body":"OK"}]},
    "tcp": {"port":19193,"request_hex":"...","response_hex":"..."},
    "udp": {"port":19090,"request_hex":"...","response_hex":"..."},
    "mqtt": {"port":1883,"topics":["review/#"]}
  },
  "setup_inputs": [
    {"kind":"button","control":"b","action":"hold","seconds":2}
  ],
  "assertions": [
    {"type":"dhcp_lease"},
    {"type":"dns_query","name":"example.test"},
    {"type":"http_request","method":"GET","path":"/api/status"}
  ],
  "timeout_seconds": 90,
  "capture_pcap": true
}
```

`setup_inputs` 必须在同一 guest 执行（如按住 B 开 web server），再等待网络事件；
不能只启动一个空窗口。

响应 `GET /sessions/{id}/network` 需要：

```json
{
  "status": "PASS|FAIL|PARTIAL|NOT_USED",
  "data_plane": "PASS|FAIL|PARTIAL",
  "isolation": "userspace-fixture-only",
  "events": [
    {"type":"wifi_auth","status":"PASS"},
    {"type":"dhcp_lease","ipv4":"192.0.2.15"},
    {"type":"dns_query","name":"example.test"},
    {"type":"tcp_connect","dst":"192.0.2.2:19193"},
    {"type":"http_request","method":"GET","path":"/api/status","status":200}
  ],
  "assertions": [{"type":"dhcp_lease","status":"PASS"}],
  "pcap_sha256": "...",
  "fixture_log_sha256": "..."
}
```

判定语义：

- `PASS`：所有 required assertions 观测到；
- `FAIL`：明确失败（M2 MIC 拒绝、DHCP/DNS/TCP/HTTP 错误）；
- `PARTIAL`：窗口内没有任何有效网络事件（应用没尝试，或 setup 未执行）；
- `NOT_USED`：固件没有网络代码/明确离线；不要用 `PARTIAL` 掩盖。

### P1：板卡覆盖

| 设备 | 需求 |
| --- | --- |
| Cardputer / Cardputer-ADV | 统一 `features.network=true`；review-sta + fixtures/events/隔离声明；覆盖 Bruce/Evil/Flipper/META TV/玄机OS 等 |
| StickS3 | review-sta + fixtures/events；支持 hold B 开 web server 等 setup |
| StopWatch | 通用 review-sta（S3 Wi-Fi） |
| PaperDIY / PaperS3 | S3 Wi-Fi 模型 + review-sta（EPD 不阻塞网络） |
| Tab5 | C6 伴生/SDIO 网络可做则做；否则 capability 标 `network: unsupported`，审查侧不再转人工 |
| StickC Plus2 / Core2 | 按流量补 classic Wi-Fi；至少 Bruce 1.17 有明确 PASS/FAIL |
| AtomS3 / AtomS3R / C6 | 视流量补 |
| ESP-NOW/BLE/LoRa | 独立 peer/fixture；LoRa/Meshtastic 若无法建模，标 `external_dependency` |

### P1：控制固件与验收

每板四类对照：

1. known-good：连接 → DHCP → DNS → HTTP GET →（可选）MQTT publish；
2. known-bad：错误 WPA2 密码 → M2 MIC 拒绝/无 DHCP；
3. setup-required：hold B 开 web server → HTTP fixture 收到请求；
4. no-network：不联网固件不得被判 `PARTIAL`。

验收标准：

- known-good `status=PASS`、`data_plane=PASS`，事件链完整；
- known-bad `status=FAIL`，错误码区分 auth/DHCP/DNS/TCP/HTTP；
- setup-required 同 guest 输入后 `PASS`；
- pcap 无 fixture 外流量；
- 当前 11 条 `E_NETWORK_PARTIAL` 重跑不再出现
  `worker_namespace_unavailable` / `board_not_advertised`。

### P2：外部依赖边界

真实 deauth/evil twin/monitor-mode RF、LoRa/Meshtastic 对端、NFC 卡、红外电视、
真实手机配网、BadUSB 主机等，不应统一转人工。能提供固定 peer 的（ESP-NOW、MQTT、
HTTP portal、BLE HID/NUS）就自动验证；不能提供的标
`NOT VERIFIED (external dependency)`，不进入 `manual_review`。

## 3. 与审查服务的接口

建议模拟器提供：

- `GET /api/v1/devices/{id}/network-capabilities`：review-sta/fixtures/setup_inputs/
  isolation/pcap/timeout；
- `POST /api/v1/sessions` 的 `network` 支持 fixtures/setup_inputs/assertions；
- `GET /api/v1/sessions/{id}/network` 返回 events/assertions/pcap/fixture log；
- 稳定失败码：`wifi_auth_failed`、`dhcp_timeout`、`dns_failed`、`tcp_refused`、
  `http_status`、`no_network_activity`、`fixture_rejected`。

审查服务会据此直接判 PASS/FAIL，不再依赖 `native_sta_worker_ready()` 的 Linux
namespace；如果需要保留 namespace，则必须提供可直接调用的 Linux worker 能力，
而不是让审查服务自建 namespace。

## 4. 关联

- 需求 issue：[#238](https://github.com/m5agent/m5stack-esp-emulator/issues/238)
- 审查侧过程诊断：
  `records/firmware-review-service/2026-11-23-review-process-diagnosis/`
- 现有模拟器文档：`docs/device-service-api.md` 的 qemu-wifi / native STA /
  HTTP/UDP/TCP fixture / SoftAP 章节。

## 5. 未覆盖项

- 模拟器实现与验收：`NOT RUN`。
- 通用 Linux worker / 便携 userspace 后端：`NOT RUN`。
- 11 条网络任务重跑：`NOT RUN`。
- 真实 RF/LoRa/NFC/手机配网：`NOT RUN`。

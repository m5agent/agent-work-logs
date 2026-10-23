# ESP Emulator P0 网络 CI、虚拟 radio 恢复与 eFuse 安全证据报告

## 背景

活动 P0 包含三条主线：

- 网络 namespace、DNS/egress、pcap、错误密码、断线和重连；
- Core2 cache/PSRAM、原生 BT controller、DNS/公网；
- FirmwareManifest、WebBurner 导入、安全配置和 capability mismatch。

既有功能大多已实现，但仍有三处缺口：

1. GitHub CI 只跑少量 catalog/profile 测试，没有执行完整平台测试和 Linux
   namespace policy；
2. reconnect 证据包含 guest disconnect 与 link down/up，但不是 WiFi 模型
   的 radio/AP 消失；
3. manifest 虽解析 sdkconfig，却没有独立的 eFuse 摘要层，也没有把配置态和
   声称的设备态分开。

## 改动

### Linux policy CI

- 完整平台测试改为 CI job；
- 新增 Ubuntu `network-namespace-policy` job；
- 安装 `iproute2`/`nftables`，启用 IPv4 forwarding；
- 执行 exact IPv4 IP/协议/端口、veth/NAT、允许/拒绝和清理 fixture；
- evidence artifact 保留 14 天。

### 虚拟 radio/AP 丢失

QEMU S3/classic ESP32 WiFi 模型已有 `radio-enabled` QOM bool。Device Service
新增 `network-fault.target=radio`：

- 在 `/machine/unattached` 中定位真实 WiFi QOM child；
- 检查 `radio-enabled` 属性存在；
- 通过 QOM 设置停止/恢复 beacon、管理帧和网络接收；
- 兼容默认 `target=link` 的原有 `set_link` 行为；
- 记录 target、QOM path、旧/新状态和 QMP 结果。

StickS3 reconnect probe 增加 radio-down scan 和 restored scan。实测：

```text
RECONNECT SCAN 1
RECONNECT DHCP 1 <guest-address>
RECONNECT HTTP /before HTTP/1.0 200 OK
RECONNECT DISCONNECTED
RECONNECT RADIO_DOWN_SCAN 0
RECONNECT RADIO_RESTORED_SCAN 1
RECONNECT DHCP 2 <guest-address>
RECONNECT HTTP /after HTTP/1.0 200 OK
RECONNECT RESULT: PASSED
```

pcap 摘要包含两组 DISCOVER/OFFER/REQUEST/ACK，HTTPS 不在本 fixture
声明范围内。

### eFuse 安全证据

FirmwareManifest 新增：

- 识别 `efuse-summary.json`、`espefuse-summary.json`、
  `efuse_summary.json`；
- 容忍 espefuse stdout 中的版本与命令 banner；
- 只提取 secure boot、Flash Encryption、secure version、key purpose 和
  write-disable；
- 不复制原 eFuse JSON，不保留 key raw value/value；
- 分开记录 `secure_boot` / `secure_boot_config`、
  `flash_encryption` / `flash_encryption_config`；
- 新增 `disabled` 状态；
- 配置启用但 eFuse 未显示启用时产生结构化 warning；
- 包内 eFuse summary 永远标记 `efuse_summary_unverified`；
- Device Service 继续拒绝没有建模安全启动/加密链的 QEMU profile。

## 验证

本机：

```text
platform tests                 239/239 PASS
runtime coverage               PASS
peripheral catalog             PASS
QEMU profiles                  PASS
git diff --check               PASS
```

GitHub Actions `39998176148`：

```text
platform-contracts             PASS
network-namespace-policy       PASS
```

radio/AP fixture：

```text
scan down / restored           0 / 1
DHCP leases                    2
HTTP before / after            200 / 200
network marker status          PASS
pcap status                    PASS
pcap DHCP DORA transactions    2
```

eFuse fixture：

```text
real espefuse v5.6 virtual summary   89 fields parsed
secure boot                          v2
Flash Encryption                     enabled
raw key/value retained               false
source eFuse JSON copied             false
capability preflight                 REJECTED (not modeled)
```

## 验证边界

- radio/AP 是 QEMU WiFi 模型状态，不是物理 RF、信道或天线；
- eFuse summary 是调用者提供的包内证据，不是真机在线读取；
- 本轮没有执行 Core2 native controller、双设备 fabric、外部 IPv6；
- 物理硬件和真机安全链仍为 `NOT RUN`。

## 风险与回滚

- `target=radio` 仅在模型暴露 `radio-enabled` 时可用，否则结构化拒绝；
- eFuse summary 解析是白名单式提取，不执行或信任其他字段；
- 回滚结果提交 `829d64e99ae318c6d78de0729bb6a75f8455373c` 可恢复到
  `34032874250d93e01657dbe389a6a832648d172f` 的文档基线，不影响物理设备。

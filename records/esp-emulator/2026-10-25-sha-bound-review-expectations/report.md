# ESP Emulator SHA-bound 固件审查预期报告

## 背景

原 user-firmware matrix 默认假设有屏固件应显示非空首帧并响应输入。公开
OpenAI Voice Assistant 是有屏 AtomS3R 上的 network-first/headless 应用：
缺少 NVS 配置时没有 UI，补入 session-isolated NVS 后能完成 WiFi、DHCP、
DNS 和 TCP/443，但不会渲染 provisioning frame。

继续用 UI/input 作为唯一应用验收标准，会把“应用路径与预期不匹配”误写成
黑屏或固件失败，也不适合以后批量审查未知固件。

## 设计

FirmwareManifest 保持事实层，只记录镜像、分区、文件、安全和 capability。
应用验收意图放在外部
`user_firmware_expectations.schema.json` v1：

- `device_id`、`firmware_id`、`sha256` 精确绑定样本；
- `mode=ui-interactive` 保持原 frame/input 门禁；
- `mode=headless-serial` 要求 bounded required/forbidden guest markers；
- `mode=network-first` 额外要求 network status PASS，并在 `capture_pcap=true`
  时要求 finalized pcap summary 和 SHA；
- 可选 `runtime`、`ready_marker`、network 配置、NVS fixture 和 bounded
  network observation window；
- `wifi_password` 明文禁止，使用 `wifi_password_env` 从 worker 环境注入；
- expectation digest、schema/file SHA、NVS/SD fixture SHA 进入结果键。

如果 selected firmware SHA 变化，旧 expectation 不会静默沿用，而是报告
SHA mismatch。没有匹配 expectation 的样本继续使用 UI 默认规则。

## 执行流

1. matrix 解析公开固件并重算 SHA；
2. 加载 expectation，检查 unknown fields、模式约束、marker 上限、
   runtime、network 字段和 NVS 镜像；
3. 精确匹配 selected device/firmware/SHA；
4. 上传固件与可选 NVS fixture；
5. 按 expectation 创建 Device Service session；
6. 采集串口、必要 frame/input 和 network evidence；
7. network-first 在 classification 前停止 session，再读取 finalized
   `/sessions/{id}/network` 与 pcap summary；
8. 结果绑定 firmware、expectation、NVS/SD fixture 和 session。

## 真实运行

公开样本：

- OpenAI Voice Assistant For AtomS3R；
- source SHA
  `b3597fcabbff57c98618caa8754af84745e9eac35b2868ab3c4cb0935b7c59b3`；
- normalized Flash SHA
  `991b1cf328bec7677ed1335d567bfcb7b6c941c1bd6b658eb991b84940b3ce8d`；
- Open NVS fixture
  `14f0acc47e1e1bef7e19d29c90febd0fe3707599fd8fc42eeb14dd27cfc26e5d`。

运行参数：

```text
runtime=qemu-wifi
profile=generic-observe
wifi_auth=open
mode=network-first
network_observe_seconds=8
```

结果：

```text
status=PASS
status_reason=network-first_expectation_ok
required markers: wifi:connected with myssid, got ip:
network status: PASS
pcap: 37 packets
DNS: api.openai.com.
TCP/443 flows: 1
stop state: stopped
```

这是 Device Service 验证的 virtual-device 行为，不是云端业务成功或 RF
验证。

## 验证

```text
platform tests              387/387 PASS
documentation contracts     20/20 PASS
Node upload/SHA             PASS
runtime coverage            PASS
peripheral catalog          PASS
QEMU profiles               PASS
project snapshot            PASS
Ruff fatal checks           PASS
compileall / diff check     PASS
GitHub Actions              PASS
```

CI `40139992678` 的 `platform-contracts` 与
`network-namespace-policy` 均成功。

## 验证边界

- 本次是 virtual-device validation；
- 使用 synthetic open WiFi password 和 synthetic OpenAI key；
- 未验证真实 OpenAI 账号、Realtime/WebRTC、音频输入输出或云端成功；
- 未验证 WPA3、group-key multicast、物理 RF 或真机；
- expectation 是人工审查意图，binary 本身不能自动推断应联网还是应显示 UI；
- 完整 QEMU 外设矩阵本轮未重跑，目标是 generic S3 network-first 路径。

## 风险与回滚

主要风险是 operator 写了错误 expectation，或把应用自身 required marker
设得过宽。当前约束要求 marker 非空、bounded、required/forbidden 不重叠，
network-first 必须有 network status 和可选 pcap，UI 默认规则不能被放宽。

回滚结果提交 `351eb16d49f1ffbef562810668f3248e1cfc7f52` 到
`e41bfd5b2e4dd0b582e1caa946d2245a67a37218` 会恢复 UI-only matrix，
不影响物理设备或生产凭据。

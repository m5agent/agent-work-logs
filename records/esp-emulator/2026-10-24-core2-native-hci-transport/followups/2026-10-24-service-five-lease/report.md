# Core2 native HCI Device Service 五 lease 报告

## 背景

`HCI-3b` 已证明 stock Core2 固件能够通过 QEMU native-HCI、固件 HLI
queue/IRQ 和 API-boundary H2C 完成外部 NUS GATT。但当时仍有两个问题：

1. 这些检查主要在独立 runner 中完成，还没有覆盖真实 Device Service
   lease、evidence ZIP 和 session 生命周期；
2. 多个入口文档仍把 `HCI-4` 写为开放，并把 GDB-mediated
   `core2-native-vhci` 描述成主要服务路径。

本轮目标是让同一 stock 固件路径进入 `/api/v1`，连续多次验证，并把当前
状态、Backlog、API/OpenAPI、代码地图和专题页统一到已完成的事实。

## 实现与改动

- Device Service 新增规范 profile `core2-native-hci`；
- Device Service 从匹配 ELF 解析 QEMU API/HLI hook 地址，不启动 GDB；
- 同一个 `qemu-unified` guest 保留 OpenMAC WiFi、显示 frame、QOM、音频、
  公网访问、外部 NUS GATT 和 pcap；
- 新增 `run_service_5x.py`，通过公开 API 创建独立 lease，输出无 session/
  artifact ID 的聚合 evidence；
- `core2-native-hci` 排在 Core2 `network_profiles` 首位；
- `core2-native-vhci` 明确标记为 legacy/diagnostic；
- 文档一致性测试要求 HCI-4 evidence、OpenAPI enum、5/5、frame/QOM/
  network/evidence checks、`gdb_bridge=false` 和 profile 文案；
- Backlog 删除已完成的 `CORE2-01`，只保留 `CORE2-02`：
  controller/baseband、cache/PSRAM、coexistence/soak、换固件验证和真机。

## 执行

五个独立服务 lease：

```text
profile=core2-native-hci
runtime=qemu-unified
API=/api/v1
attempts=5/5 PASS
gdb_bridge=false
frame=320x240
qom_nodes=27
wifi_dhcp_http=PASS
public_dns_http=PASS
external_nus_gatt=PASS
pcap=present
evidence_zip=PASS
```

完成文档和 runner 输出整理后，再次启动临时 Device Service，使用同一固件、
ELF 和 QEMU build 实跑：

```text
updated runner recheck=1/1 PASS
frame_sha256=5bfcdf8fc518a36385783a9b5bf09b3fbce9d8c07406326955569f6c7db8408b
```

本地与 CI：

```text
local platform tests       283/283 PASS
GitHub Actions             Ran 283 tests; OK (skipped=2)
network namespace policy   PASS
Node SHA256/upload         2/2 PASS
runtime coverage           PASS
peripheral catalog         PASS
QEMU profiles              PASS
OpenAPI YAML               PASS
```

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | `NOT RUN` | 本轮复用已验证 QEMU build，未重新构建 QEMU |
| transport | `PASS` | QEMU native-HCI + HLI/ACL，无 GDB bridge |
| device_response | `PASS` | 外部 Bumble NUS write 和 guest notify ACK |
| data_behavior | `PASS` | WiFi/DHCP/HTTP、公网、frame、QOM 和 pcap 同一 lease |
| visual_or_physical | `NOT RUN` | 没有物理显示器、RF 或电气测量 |
| review/delivery | `PASS` | 源码、文档、OpenAPI、CI 和工作记录已对齐 |

## 边界

- 当前 hook 指令偏移只对已验证的 UIFlow2 v2.5.3 build 成立；
- Device Service 要求来自同一固件构建的匹配 ELF；
- 其他 Core2 固件不能继承该 PASS；
- `core2-native-hci` 仅支持 trusted-host isolation，不等于恶意固件沙箱；
- 不是 bit-exact BT controller/baseband，也不是 RF、物理 cache/PSRAM、
  coexistence 或长期稳定性证明；
- GDB legacy profile 的 `1/2` 失败记录继续保留，不写成稳定能力。

## 风险与回滚

回滚源码提交
`de5a6c737548c88ade1e318d424da254e3d0778c` 会移除新 profile、runner、
evidence 和文档对账，不修改 QEMU worktree、固件或 Device Service 历史。
仓库未提交固件、ELF、QEMU 二进制或 session 标识。

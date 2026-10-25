# ESP Emulator 代码、文档与当前工作/待办收口

- 日期：`2026-10-25`
- 结果：`PASS`（docs/contracts；能力边界仍按 `project-status.md`）
- 工作类型：`docs_change`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 基线版本：`3f4bf92b96d5854f0804d7f7014c4a9c244da99e`
- 能力提交：`08d8a21bda173ff65dfb5343d0fa8082732eb872`
- 文档边界提交：`e41bfd5b2e4dd0b582e1caa946d2245a67a37218`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40138787543>
- 环境：macOS Apple Silicon；Python 3；GitHub Actions Ubuntu

## 结论

当前状态、Backlog、工作流、代码地图、验证台账、运行时缺口、Device
Service API、网络和用户固件文档已收敛到同一组事实源。文档不再把
Open-only WiFi、未验证 IPv6 或尚未关闭的 `RUNTIME-05` 当作当前结论。

后续在 `6120489` 上进一步补齐测试/补丁总索引、自动代码规模快照和一页式
交接，见
[Follow-up: code/document inventory and handoff](followups/2026-10-25-code-doc-inventory-and-handoff/)。

2026-10-25 后续又补齐 Core2 guest PSRAM 分配/三轮读回，并把当前状态、
Backlog、代码地图和设备元数据改为只引用同一份证据，见
[Follow-up: Core2 PSRAM and current-doc reconciliation](followups/2026-10-25-core2-psram-doc-freshness/)。

本轮同时关闭了 accepted virtual-device scope 内的 S3 WPA2-PSK 数据面：
正确密码完成 RSN/M1-M4/CCMP、DHCP、DNS 和 TCP/443；错误密码在 M2 MIC
被拒绝且没有 DHCP。详细实现、证据和剩余边界见
[S3 WPA2-PSK 记录](../2026-10-25-s3-wpa2-psk-data-plane/)。

最后一轮一致性检查还修正了 `AGENTS.md` 中两条过期稳定边界：

- Linux exact endpoint policy 已同时覆盖 IPv4 与 IPv6，不再写成 IPv4-only；
- virtual S3 WPA2-PSK 的证明范围已明确为 RSN/EAPOL/pairwise CCMP 和 guest
  DHCP/DNS/TCP，不再与 WPA3-SAE、group multicast 或物理 RF 混算。

2026-10-25 后续新增面向接手人的工程交接页，统一代码阅读顺序、成熟度、
当前工作流和 P0 下一步，并修正 UIFlow2 全矩阵页的相对时间措辞，见
[Follow-up: engineering handoff and documentation freshness](followups/2026-10-25-engineering-handoff-and-freshness/)。

## 当前结论

- 当前实现：共登记 14 台设备；13 台达到登记外设的 `simulated`，Tab5
  为 `partial`；Device Service 管理 12 台 QEMU ESP32 和 Tab5，当前共有
  14 个 unified profile。
- 网络：单 guest、双 guest、namespace、controlled DNS、TLS allowlist、
  exact IPv4/IPv6 egress、pcap、断线重连、worker-local QEMU 和
  HTTPS/mTLS worker 控制面已有可执行证据。
- Core2：WiFi、公网 DNS/HTTP、native-HCI、same-guest GATT 重连、
  active-BLE 与限容 TCG soak 已通过 virtual-device 验证。
- 固件审查：Manifest/WebBurner、capability/security preflight、静态/SBOM、
  LittleFS/FAT/SPIFFS 和 session-isolated SD/NVS fixture 已可用。
- 真机、RF、功耗、声学、光学、机械和电气验证仍为 `NOT RUN`。

## 仍待完成

1. `NET-04` / `SVC-01`：自动主机发现、跨主机 QEMU executor/reattach、
   companion/evidence continuity 和多机调度。
2. `CORE2-02`：bit-exact controller/baseband、物理 cache/PSRAM、
   长时吞吐/teardown 和真机同路径。
3. `FW-01/02/03`：运行态权限/许可、生产安全配置、headless/cloud 执行预期
   和更多固件族。
4. `RUNTIME-02/03/04`：C6 Zigbee commissioning、Core2 legacy I2C routing
   和 ATECC608 fixture。
5. `HW-01`：代表设备同固件 SHA 的真机验证。
6. 后续：`SVC-02/03`、`TAB5-01`、`UI-01`、`CZ-01`。

## 关键证据

- 平台测试：`377/377 PASS`；
- 文档契约：`20/20 PASS`；
- runtime coverage、peripheral catalog、project snapshot：`PASS`；
- `git diff --check`：`PASS`；
- CI `platform-contracts` 与 `network-namespace-policy`：`PASS`；
- 本轮源码差异：`28` files、`1954` insertions、`135` deletions，其中
  WPA2 功能提交与最终文档边界提交分开保留；
- 本轮未重新执行完整 QEMU 功能矩阵；目标 S3 回归为 `15/15`，见 WPA2
  功能记录；物理硬件 `NOT RUN`。

## 文件

- `report.md`：整理原则、状态纠偏、工作/待办、验证与边界；
- `run.json`：机器可读记录；
- `evidence/verification.summary.json`：脱敏验证摘要。

# agent-work-logs

`m5agent` 的工作记录仓库，分两层发布。

| 层 | 目录 | 发布目标 | 内容 |
| --- | --- | --- | --- |
| 对外 | `records/` | 内部 GitLab + 公开 GitHub | 公开仓库的 Issue 处理、PR/MR 评审、公开库的硬件或构建验证、可复现缺陷分析 |
| 内部 | `internal/` | **仅内部 GitLab** | 内网运维、环境配置、权限盘点、服务部署、内网服务排查 |

两层内容互不混合。公开层会原样出现在公开仓库，因此公开层里不允许出现任何内网信息。

## 发布

```bash
./scripts/publish.sh
```

脚本做两件事：

1. 把完整仓库（含 `internal/`）推送到内部 GitLab。
2. 把公开子集（`records/`、`docs/`、`templates/`、根文件）重建为单个提交，强制推送到公开 GitHub。

公开仓库由公开子集同步而来，保留**线性追加历史**（不重写），因此对外记录可以安全地用固定 commit permalink 引用。

## 判断该放哪一层

只要回答一个问题：**这条记录对外部读者有价值吗？**

- 有价值 → `records/`
- 只是本机或内网的操作记录 → `internal/`
- 拿不准 → 放 `internal/`。宁可少公开，也不要把内网细节推出去。

配置企业微信、安装本机工具、调整访问控制、盘点内网权限这类操作，都属于 `internal/`。

## 记录格式

- [工作流](docs/work-record-workflow.md)
- [记录格式](docs/record-format.md)
- [脱敏规则](docs/redaction-policy.md)
- 模板：[templates/work-record/](templates/work-record/)

## 结果等级

`PASS` / `PARTIAL` / `FAIL` / `NOT RUN` / `REVIEW`。一条记录可以同时包含多个层级结果，
不要用单一总状态掩盖未覆盖项。

## 对外记录索引

| 2026-09-18 | m5stack 公开仓库 | 公开仓库零评论 Issue 盘点与可回复性评估 | REVIEW（盘点）+ PARTIAL（5 条 host/编译级闭合验证） | [查看](records/m5stack-github/2026-09-18-recent-unanswered-issues/) |
| 2026-09-21 | ESP32-P4 Flasher | 可配置 DUT 烧录波特率，默认 1.5 Mbaud | PARTIAL（构建/中心测试通过；实机烧录未执行） | [查看](records/esp-flasher-by-esp32p4/2026-09-21-configurable-flash-baud/) |
| 2026-10-10 | UIFlow MicroPython | StamPLC `boot_option=2` Wi-Fi 启动跳过 PoE 初始化 | PARTIAL（host 复现 + 构建 PASS；无 StamPLC 实机） | [查看](records/m5stack-github/2026-10-10-uiflow-issue-116-stamplc-wifi/) |
| 2026-10-10 | UIFlow MicroPython | RTC 同步改用 UTC，修复重启时钟漂移 | PASS（StopWatch 实机 + 构建；StamPLC 未单独复测） | [查看](records/m5stack-github/2026-10-10-uiflow-issue-117-rtc-utc/) |
| 2026-10-10 | m5stack-linux-dtoverlays | aw882xx 支持 Linux 6.13+ 头文件 | PARTIAL（6.12/6.14 构建 PASS；未做 insmod/音频） | [查看](records/m5stack-github/2026-10-10-dtoverlays-issue-14-aw882xx-kernel/) |
| 2026-10-23 | ESP Emulator | Device Service 单实例 unified runtime 与 OpenAPI 契约统一 | PASS（API contract + 172 tests + live service；物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-unified-device-api-contract/) |
| 2026-10-23 | ESP Emulator | 固件 SoftAP 配网 API 与 loopback portal 验证 | PARTIAL（virtual-device：AP 关联、DHCP、portal GET、停止取证 PASS；表单/NVS/STA/物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-softap-provisioning-api/) |
| 2026-10-23 | ESP Emulator | ESP32-S3/C6 单 guest 公网 WiFi、BLE 与全外设矩阵 | PASS（virtual-device validation：67/67 matrix + Device Service lease；物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-c6-unified-wifi-ble/) |
| 2026-10-23 | ESP Emulator | 项目状态、设备档案与 Backlog 收敛 | PASS（182 tests + generated docs/link/API consistency；未改 QEMU 数据面） | [查看](records/esp-emulator/2026-10-23-project-status-docs-consolidation/) |
| 2026-10-23 | ESP Emulator | P0 网络、固件入口与 Core2 稳定性/无线 | PARTIAL（virtual-device：namespace/pcap/reconnect、FirmwareManifest、Core2 10/10 与公网/HCI GATT；原生 BT 与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-p0-network-firmware-core2-closure/) |
| 2026-10-23 | ESP Emulator | Core2 stock native-VHCI BLE GATT | PASS（virtual-device：外部 NUS GATT 5/5；生产化 VHCI、bit-exact controller 与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-core2-stock-vhci-gatt/) |
| 2026-10-23 | ESP Emulator | Core2 同 guest WiFi + stock native-VHCI BLE | PASS（virtual-device：board/WiFi/公网/frame/QOM/native-VHCI 3/3；Device Service 与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-core2-unified-native-vhci/) |
| 2026-10-23 | ESP Emulator | Core2 native-VHCI 接入 Device Service | PASS（virtual-device：单 lease 18/18 checks、frame/QOM/pcap/evidence PASS；GDB 后端与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-core2-native-vhci-service/) |
| 2026-10-23 | ESP Emulator | Core2 零重试确定性矩阵与 RTC 虚拟时钟 | PASS（virtual-device：67/67、274/274，全部首轮无重试；Core2 6/6、重复 5/5、UI flash/touch PASS；物理等价性与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-23-core2-zero-retry-rtc/) |
| 2026-10-23 | ESP Emulator | FirmwareManifest 脱敏静态审查与 SBOM | PASS（3/3 真实公开固件 round-trip；URL query、凭据、编码值和宿主路径未进入 manifest；文件系统策略与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-23-firmware-static-review/) |
| 2026-10-23 | ESP Emulator | 文档、状态与执行任务板总整理 | PASS（当前事实/历史证据分层、Core2 状态纠偏、215/215 平台测试；7823bef 后全矩阵与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-documentation-reconciliation/) |
| 2026-10-23 | ESP Emulator | Host allowlist fixture、TLS blocker 与文档二次对账 | PARTIAL（223/223 平台测试、契约与文档一致性 PASS；guest TLS 因 AES/GDMA FAIL；Linux namespace TLS 与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-23-network-docs-reconciliation/) |
| 2026-10-24 | ESP Emulator | ESP32-S3 GDMA、controlled DNS 与 TLS Host allowlist | PASS（virtual-device：Linux namespace DNS A/NXDOMAIN、TLS 允许 200/拒绝 403、后台域名拒绝和 pcap PASS；67/67 矩阵全部首轮；物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-tls-gdma-external-memory/) |
| 2026-10-24 | ESP Emulator | FirmwareManifest LittleFS 文件清单与敏感资源脱敏 | PASS（static-image：真实 StickS3 sys/vfs 文件哈希、敏感路径、SPDX 与 manifest round-trip；SPIFFS/FAT/权限与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-firmware-littlefs-inventory/) |
| 2026-10-24 | ESP Emulator | FirmwareManifest FAT12/16/32 只读文件清单 | PASS（static-image：三种 FAT、LFN、多簇哈希、敏感路径、循环链、malformed/erased 与 Manifest 集成；真实 PaperColor FAT12 PARTIAL；SPIFFS/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-fat12-16-32-inventory/) |
| 2026-10-24 | ESP Emulator | 精确 IPv4 IP/端口 egress、veth/NAT 与清理 | PASS（Linux namespace：nftables 默认 drop、允许/拒绝 IP+端口、`1.1.1.1:80` 公网 NAT、TLS guest 200/403/pcap；外部 IPv6 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-ip-port-egress-allowlist/) |
| 2026-10-24 | ESP Emulator | DHCP lease renewal through Device Service | PASS（virtual-device：ESP-IDF `netifapi_dhcp_renew`、DORA→REQUEST/ACK、renewal request/ack 各 1、地址保持、HTTP 200；真实 AP 丢失与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-dhcp-renewal/) |
| 2026-10-24 | ESP Emulator | 当前基线、代码地图、网络方案与 Backlog 重整 | PASS（docs/catalog/profile：225/225 平台测试、链接/日期/旧状态契约 PASS；本次未重跑功能矩阵，物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-project-baseline-reconciliation/) |
| 2026-10-24 | ESP Emulator | 工作流台账、代码工具清单与 Task ID 一致性 | PASS（docs：12 条工作流、24 个平台工具、全部 Backlog Task ID 与 236/236 测试 PASS；本次未重跑功能矩阵，物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-workstream-inventory-consolidation/) |
| 2026-10-24 | ESP Emulator | P0 Linux policy CI、虚拟 radio 恢复与 eFuse 安全证据 | PASS（virtual/static：239/239、GitHub Actions namespace/egress、scan `1→0→1`、两次 DHCP/HTTP/pcap、脱敏 eFuse 解析与 capability 拒绝；Core2 无 GDB 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-p0-network-ci-efuse/) |
| 2026-10-24 | ESP Emulator | Core2 native-VHCI ELF 固定符号、代码与文档对账 | PASS（virtual-device：ELF/GDB 地址一致、standalone 5/5、unified 3/3、243/243）；后续 repeated lease `1/2`，C2H 注入稳定性为 FAIL | [查看](records/esp-emulator/2026-10-24-core2-pinned-vhci-symbols/) |
| 2026-10-24 | ESP Emulator | Core2 QEMU native HCI transport 与 guest H2C capture | PARTIAL（transport PASS；无 GDB 捕获 stock HCI Reset `01030c00`；C2H、完整 sequence、controller 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-native-hci-transport/) |
| 2026-10-24 | ESP Emulator | 文档新鲜度、P0 现状与 Core2 HCI 阶段重整 | PASS（docs：30 页分类、29 页日期台账、链接/旧状态契约 PASS；243 tests，本机全绿、CI skipped=2；未改运行数据面） | [查看](records/esp-emulator/2026-10-24-project-docs-hci-stage-reconciliation/) |
| 2026-10-24 | ESP Emulator | Core2 QEMU native HCI 单包 C2H callback 交付 | PARTIAL（virtual-device：Reset Complete callback 后 guest 发出 `01011000`，targeted 5/5；完整 HCI/GATT、repeated lease、controller 与真机 NOT RUN/FAIL） | [查看](records/esp-emulator/2026-10-24-core2-c2h-callback-delivery/) |
| 2026-10-24 | ESP Emulator | 固件可恢复上传可靠性、代码与文档总整理 | PASS（service/API/docs：失败 append 回滚、staging GC、249 tests 本机全绿、CI 247 pass/2 skip；WebBurner UI、HCI-3b/HCI-4 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-firmware-upload-docs-consolidation/) |
| 2026-10-24 | ESP Emulator | WebBurner 流式固件导入、刷新恢复与取消 | PASS（browser/API：9.44 MiB / 3 chunks、manifest PASS、253 tests、Node 2/2；合成固件启动与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-webburner-browser-intake/) |
| 2026-10-24 | ESP Emulator | 代码地图、文档、工作流与 Backlog 总整理 | PASS（docs/contracts：253 tests 本地全绿、CI 253 tests with 2 skipped、Node 2/2、namespace/egress PASS；本轮未重跑功能矩阵，物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-code-doc-workqueue-reconciliation/) |
| 2026-10-24 | ESP Emulator | Core2 native HCI 完整 sequence 诊断 | FAIL（HCI-3b：广播/连接/首个 ATT PASS；ACK 12/Reset；safe-point 与真实 controller-entry 实验均回退） | [查看](records/esp-emulator/2026-10-24-core2-hci3b-diagnostic/) |
| 2026-10-23 | ESP Emulator | StickS3 公网 HTTP 闭环与第三方固件 NTP 超时定位 | PASS（virtual-device validation；NTP 应用层失败单列） | [查看](records/esp-emulator/2026-10-23-sticks3-public-network-closure/) |
| 2026-10-23 | ESP Emulator | StickS3 社区天气固件网络、显示与按键验证 | PARTIAL（virtual-device follow-up：QIO/NVS/LittleFS/实时天气/完整八页/语音已闭环；双击固件缺陷与实体硬件未通过） | [查看](records/esp-emulator/2026-10-23-sticks3-community-weather-functional/) |
| 2026-10-23 | ESP Emulator | `.work/` 运行资产缺失的部署诊断与结构化错误 | PASS（fresh clone + virtual-device session；物理硬件未测） | [查看](records/esp-emulator/2026-10-23-runtime-assets-deployment/) |
| 2026-10-24 | ESP Emulator | 双 guest 私有 lab fabric、共享 WLAN patch 与全矩阵 | PASS（virtual-device：17/17 fabric gates、双侧 DHCP/TCP/pcap、宿主隔离、260/260 平台测试、67/67 矩阵零重试；worker/IPv6/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-two-guest-lab-fabric/) |
| 2026-10-24 | ESP Emulator | 本地 worker identity、heartbeat、drain 与重启分类 | PASS（virtual-device worker control：17/17 lifecycle checks、真实 `qemu-wifi` drain、pcap availability、SIGKILL 后 generation 2 abandoned lease、264/264 平台测试；远程 worker/re-attach/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-local-worker-lifecycle/) |
| 2026-10-24 | ESP Emulator | 当前状态、验证台账、Backlog 与代码地图分层 | PASS（docs/contracts：264/264 平台测试、GitHub Actions、runtime/catalog/profile 校验、Node 2/2、9 项文档契约与 evidence JSON；完整矩阵与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-current-status-validation-ledger/) |
| 2026-10-24 | ESP Emulator | Core2 VHCI API-boundary 与 HCI-3b 事务审计 | PARTIAL（virtual-device：广播/连接/NUS discovery/subscription PASS；final write/notify 与完整 GATT FAIL；264/264 与 CI PASS；实验代码未保留） | [查看](records/esp-emulator/2026-10-24-core2-hci3b-api-boundary/) |
| 2026-10-24 | ESP Emulator | SPIFFS 只读清单、LUT 校验与当前文档对账 | PASS（static-image：8 配置、多索引、canonical/malformed、Manifest 脱敏、267 tests、Node 2/2；QEMU 矩阵与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-spiffs-inventory/) |
| 2026-10-24 | ESP Emulator | 工作流交接、代码卫生与 Core2 HLI 诊断 | PASS（docs/contracts：267 tests、Node 2/2、catalog/profile、文档契约与 Ruff PASS；HLI 仅 event-13 marker，HCI-3b/GATT/真机仍开放） | [查看](records/esp-emulator/2026-10-24-workstream-handoff-hli/) |
| 2026-10-24 | ESP Emulator | Core2 HLI 真实 Reset Complete 交付 | PASS（virtual-device narrow path：池化 HCI event 经 HLI queue/ISR/controller task 交付，`01030c00 → 01011000` 连续 5/5；ACL、完整 GATT、Device Service 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-hli-event-delivery/) |
| 2026-10-24 | ESP Emulator | FirmwareManifest 声明级许可 allowlist/denylist | PASS（static policy：provenance/FS/SBOM 声明汇总、allow/deny/unknown 状态、schema 与 272 tests、CI PASS；完整源码扫描/法律结论/运行时权限 NOT RUN） | [查看](records/esp-emulator/2026-10-24-license-policy/) |
| 2026-10-24 | ESP Emulator | 远程 worker 注册目录、文档再对账与 Core2 HLI/API 诊断 | PASS（code/API/docs follow-up：283/283 tests、12 QEMU-backed + Tab5 profile guard、Core2 NUS write 2/2 但 notification 0/2；supervisor/队列/re-attach 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-remote-worker-directory-and-work-inventory/) |
| 2026-10-24 | ESP Emulator | Core2 native HCI Device Service 五 lease 与文档总整理 | PASS（virtual-device：`core2-native-hci` 5/5、frame/QOM/WiFi/公网/NUS GATT/pcap/evidence PASS、GDB bridge absent；bit-exact controller、物理等价性、长稳与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-native-hci-transport/followups/2026-10-24-service-five-lease/) |
| 2026-10-24 | ESP Emulator | 远程 worker durable job queue 与 lease supervisor | PASS（contract/API：幂等 submit、capability claim、identity-bound lease、expiry retry、cancel/result、worker stale/stop/generation 回收、restart recovery、289/289 tests；executor/evidence 回传/QEMU re-attach/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-remote-worker-durable-queue/) |
| 2026-10-24 | ESP Emulator | 本地 QEMU/QMP restart re-attach | PASS（virtual-device infrastructure：仅 SIGKILL 服务时真实 StickS3 QEMU 存活；二代服务按 PID start-time+QMP ownership+running 状态接管同一 PID、重建 gen 2 lease 并可清理；companion/evidence/cross-host/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-qemu-restart-reattach/) |
| 2026-10-24 | ESP Emulator | HTTP-only worker executor 与真实 durable job | PASS（virtual-device：独立 agent 注册/claim/heartbeat，创建真实 StickS3 QEMU session，下载 evidence ZIP/SHA256，停止 session 并提交 completed/PASS，292/292 tests；跨主机/auth/companion/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-http-worker-executor/) |
| 2026-10-24 | ESP Emulator | Worker HMAC authentication 与签名真实 job | PASS（virtual-device：worker/generation key、timestamp/nonce/body HMAC、path/body identity binding；unsigned claim 401，签名 agent 完成真实 StickS3 job，296/296 tests；跨主机 TLS/mTLS、rotation、companion/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-worker-hmac-auth/) |
| 2026-10-24 | ESP Emulator | 当前代码/文档对账与 Core2 extended-run 失败固化 | PARTIAL（docs/contracts：296/296 tests、Node 2/2、CI PASS；Core2 `HCI-4` 功能基线仍 PASS，但 extended-run/soak 在 READY/联网/BLE 连接后 panic，根因未定；完整矩阵与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-extended-run-and-current-work-reconciliation/) |
| 2026-10-24 | ESP Emulator | 当前基线、动态文档与 QEMU/设备验证元数据收口 | PASS（docs/contracts：297/297 tests、Node 2/2、CI 全部成功；动态计数单一事实源、catalog/profile 交叉校验、AtomS3R/PaperMono 旧元数据修正；全矩阵与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-code-doc-baseline-reconciliation/) |
| 2026-10-24 | ESP Emulator | P0 网络错误密码、Core2 2×120s 与公开固件 Manifest/WebBurner | PARTIAL（virtual/static：wrong-password 7/7、DNS/UDP 5/5、Core2 2/2×120s、公开固件 merged/WebBurner 同 hash 且 camera mismatch REJECTED，299/299 + CI PASS；物理 cache/PSRAM、bit-exact controller、同 guest 重连、多小时 soak 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-p0-network-core2-firmware-progress/) |
| 2026-10-24 | ESP Emulator | StickS3 自动 radio 断线、scan 1→0→1、双 DHCP 与前后 HTTP/pcap | PASS（virtual-device：同 session 16/16 checks、pcap 9,586 bytes、299/299 tests + CI PASS；物理 RF/不同 DHCP server/硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-sticks3-reconnect-runner/) |
| 2026-10-24 | ESP Emulator | Core2 active BLE + WiFi/公网两分钟共存 | PASS（virtual-device：2/2×120s、peer 全程连接、HLI/TX queue 无错误、299/299 tests + CI PASS；同 guest reconnect、bit-exact controller、物理 cache/PSRAM、多小时 soak 与硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-active-ble-coexistence/) |
| 2026-10-24 | ESP Emulator | 代码文档重整与 Core2 同 guest reconnect 边界 | PARTIAL（docs/contracts：299/299 tests、Node 2/2、catalog/profile/coverage PASS；stock 与重广告对照均在 disconnect 后 `ack 12`/HCI reset，第二轮连接 FAIL；bit-exact controller、长稳与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-docs-reconciliation-core2-reconnect/) |
| 2026-10-24 | ESP Emulator | Core2 同 guest BLE 重连修复、120 轮扩展与 600 秒 active hold | PASS（virtual-device：3 个独立 lease 各完成 120 轮 NUS GATT，HLI 3377/3377；另 2 个 lease 保持 active BLE 600 秒，peer 未断开、HLI 45/45；池 3/9/3、无 panic，321/321 tests + CI 40087552321 PASS；>120 轮、两小时 soak、bit-exact controller、物理 cache/PSRAM 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-same-guest-reconnect-fix/) |
| 2026-10-24 | ESP Emulator | Device Service worker HTTPS/mTLS、真实 QEMU/unified job 与自动凭据迁移 | PASS（transport-security：TLS 1.3、mTLS、Bearer+HMAC、真实 QEMU/unified job；SIGHUP rotation、activity drain、A/B overlap；双 worker 通过 generation pointer 自动迁移并写 secret-free receipt，无需 worker SIGHUP，321/321 tests + CI PASS；worker 主机自动发现、跨主机、secret manager 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-worker-https-mtls/) |
| 2026-10-24 | ESP Emulator | 六机型 M5Burner 用户固件批量仿真与模型缺口分类 | PARTIAL（virtual-device：18 样本；45 秒重跑后 10 PASS/8 PARTIAL/0 FAIL，C6 Zigbee 与软件复位 chip-id 两类模型缺口结构化；StickS3 与 StopWatch 各 3/3；真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-user-firmware-six-device-matrix/) |
| 2026-10-24 | ESP Emulator | C6 软件复位 Flash 写地址与 PMP 模型修复 | PASS（virtual-device：`RUNTIME-01` 关闭，offset 0 bootloader 头保持 chip ID 13，`runtime_model_gaps=[]`，Nesso 官方外设 5/5、NanoC6 PASS、317/317 tests + CI；Meshtastic 独立应用异常、Zigbee 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-user-firmware-six-device-matrix/followups/2026-10-24-c6-soft-reset-flash-fix/) |
| 2026-10-24 | ESP Emulator | 运行时模型缺口登记、Core2 二十轮与旧文档结论总整理 | PARTIAL（历史快照：当时 `RUNTIME-01`/`RUNTIME-02` 均 OPEN；后续 C6 Flash/PMP 修复关闭 `RUNTIME-01`，Zigbee `RUNTIME-02` 继续跟踪） | [查看](records/esp-emulator/2026-10-24-runtime-model-gap-register-reconciliation/) |
| 2026-10-24 | ESP Emulator | C6 Zigbee `thread-sim` 可行性分类 | PARTIAL（virtual-device：双 C6 switch/light 产生 21+17 个双向 802.15.4 帧，协调器组网与 steering 启动；join/On-Off 未完成，分类 `runtime_model_gap`，公开固件匹配 ELF 缺失，真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-c6-zigbee-thread-sim-feasibility/) |
| 2026-10-24 | ESP Emulator | Core2 热门公开固件、PMIC I2C 与 AWS ATECC608 模型缺口 | PARTIAL（virtual-device：3 个 MOST_DOWNLOADED 官方固件均执行但黑帧；PMIC 2 个、ATECC608 1 个结构化 model gap，AXP192/2101 A/B 同错；323/323 tests + CI PASS，真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-public-firmware-model-gaps/) |
| 2026-10-24 | ESP Emulator | 项目快照生成器与代码/文档结构收敛 | PASS（docs/contracts：自动快照、动态事实去重、早期 bring-up 标历史、FW-03 修正为 7 台/21 样本；324/324 tests、Ruff、catalog/profile/coverage PASS；QEMU 功能矩阵与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-project-snapshot-doc-consolidation/) |
| 2026-10-24 | ESP Emulator | 文件权限、包内源码许可扫描与 Core2 AXP I2C 首错定位 | PASS（static/runtime diagnosis：FAT/LFS/SPIFFS permission policy、2 个源码 SPDX 声明与敏感路径脱敏、329/329 tests；AXP2101 chip-id `0x4a` PASS，后续读取未产生 address-0x34 事务，`RUNTIME-03` 仍未关闭；真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-firmware-permission-and-source-scan/) |
| 2026-10-24 | ESP Emulator | exact IPv6 egress、双栈 NAT 与代码/文档重整 | PASS（virtual-network policy：IPv4/IPv6 allowed/denied endpoint、IPv6 neighbor control、双栈 masquerade 与全部 cleanup；本地 2/2、336/336 tests、Node 2/2、GitHub Actions PASS；固件、公网 IPv6、CIDR/domain、IPv6 DNS、Core2 两小时 soak 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-dual-stack-egress-and-doc-reconciliation/) |
| 2026-10-24 | ESP Emulator | A/AAAA resolver、IPv6 预检与 WebBurner capability intake | PASS（contract/static：A/AAAA resolver、IP/v6 preflight、required/optional capability API/Browser、`camera`-on-StickS3 409、sdkconfig WiFi/BT/PSRAM detected warning；340/340 tests、Node 2/2、三个 CI PASS；同 guest IPv6 DNS/HTTP、reported=actual code path 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-dual-stack-egress-and-doc-reconciliation/followups/2026-10-24-dns-aaaa-and-capability-intake/) |
| 2026-10-24 | ESP Emulator | 跨 network namespace worker 控制面 | PASS（transport-control：真实 service/worker 经 veth、Bearer+HMAC 注册、submit/claim、双 heartbeat、terminal completed、token 不落日志与 cleanup；本地+CI PASS；QEMU executor/reattach、companion continuity、多机调度与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-dual-stack-egress-and-doc-reconciliation/followups/2026-10-24-cross-netns-worker-control-plane/) |
| 2026-10-24 | ESP Emulator | Core2 两小时功能 soak、同 guest IPv6 与当前文档重整 | PARTIAL（virtual-device：artifact-bound `7200s` 功能 PASS 但 host RSS `+458016 KiB` 为 REVIEW；测试构建完成同 guest IPv6 TCP/HTTP；controlled AAAA/denied-port、物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-soak-ipv6-doc-reconciliation/) |
| 2026-10-25 | ESP Emulator | 当前状态、代码边界与执行队列重整 | PASS（docs/contracts：349/349 tests、Node 2/2、catalog/profile/coverage/snapshot、Ruff fatal PASS；Core2 限容两小时、121 轮、IPv6 namespace 与刷新固件功能重跑、真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-soak-ipv6-doc-reconciliation/followups/2026-10-25-docs-code-handoff/) |
| 2026-10-25 | ESP Emulator | Worker control/runtime API 平面拆分 | PARTIAL（control/runtime 双端点、session 请求路由单测、Linux namespace control-plane 13/13、350/350 tests；worker-local QEMU fixture 已准备但 NOT RUN） | [查看](records/esp-emulator/2026-10-24-http-worker-executor/followups/2026-10-25-control-runtime-plane-split/) |
| 2026-10-25 | ESP Emulator | Firmware required/optional capability 一致性 | PASS（static-manifest：重叠拒绝、required mismatch 拒绝、optional mismatch warning、未知项 warning；22/22 manifest + 350/350 platform；运行代码路径与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-webburner-browser-intake/followups/2026-10-25-required-optional-capability-consistency/) |
| 2026-10-25 | ESP Emulator | Firmware security evidence 冲突检查 | PASS（static-security：config/eFuse 双向冲突、v1/v2 mismatch、secure-boot/XTS key purpose 缺失 warning；CI PASS；真实 eFuse/secure boot/Flash Encryption 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-webburner-browser-intake/followups/2026-10-25-required-optional-capability-consistency/followups/2026-10-25-security-evidence-conflicts/) |
| 2026-10-25 | ESP Emulator | 公开固件 refresh、resume 与 SHA 绑定 | PARTIAL（static/contracts：首次与 resume 均强制刷新，结果键含 SHA，当前 4 样本 static/manifest 4/4 PASS、review REVIEW_REQUIRED；351/351 tests + CI；Device Service 功能与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-user-firmware-six-device-matrix/followups/2026-10-25-public-artifact-refresh-binding/) |
| 2026-10-25 | ESP Emulator | Core2 限容两小时 active-BLE host-memory soak | PASS（virtual-device：1/1 lease、资产/工具哈希无漂移、功能/HLI/pcap/cleanup 全 PASS；240 采样 RSS 323536→252992 KiB、phys 250880→188416 KiB；121 轮、物理 cache/PSRAM 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-soak-ipv6-doc-reconciliation/followups/2026-10-25-bounded-7200s/) |
| 2026-10-25 | ESP Emulator | 当前工作/文档总整理与 Core2 单 lease 121 轮 reconnect | PASS（docs/contracts：355/355、19/19 docs、Node 2/2、三个 CI；virtual-device：readiness 与 accelerator sampling 修复后 1/1 lease、121/121 cycles、HLI 3405/3405、零错误/panic；3/3、物理 cache/PSRAM 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-soak-ipv6-doc-reconciliation/followups/2026-10-25-reconnect121-doc-reconciliation/) |
| 2026-10-25 | ESP Emulator | Core2 三 lease 121 轮、guest IPv6 namespace 与当前 Backlog 重整 | PASS（virtual-device + docs/contracts：3/3×121、controlled AAAA/IPv6 HTTP/denied-port/cleanup、355/355、19/19、Node 2/2；物理 cache/PSRAM、bit-exact controller、吞吐/teardown、真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-core2-soak-ipv6-doc-reconciliation/followups/2026-10-25-three-lease-ipv6-current-state/) |
| 2026-10-25 | ESP Emulator | 四个当前公开固件的 Device Service 功能重跑 | PARTIAL（virtual-device：2 PASS/2 PARTIAL/0 FAIL；XiaoZhi 配网 UI、EDC 启动页 PASS；OpenAI 黑屏、CrossPoint SD fixture gap；物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-user-firmware-six-device-matrix/followups/2026-10-25-refreshed-four-functional/) |
| 2026-10-25 | ESP Emulator | Session-isolated FAT32+MBR SD fixture 与 CrossPoint closure | PASS（virtual-device：3 PASS/1 PARTIAL/0 FAIL；CrossPoint 进入主菜单、storage SHA 纳入结果键、service restart/evidence restore PASS；OpenAI 黑屏与物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-user-firmware-six-device-matrix/followups/2026-10-25-refreshed-four-functional/followups/2026-10-25-sd-mbr-fixture/) |
| 2026-10-25 | ESP Emulator | OpenAI 首次启动 NVS 前置条件、generic S3 WiFi 与状态文档重整 | PASS（virtual-device fixture：公开 NVS 全空，Open fixture 完成关联/DHCP/DNS/TCP 443，session-isolated overlay 与 13/13 checks PASS；376/376 tests、20/20 docs、Node 2/2、CI PASS；RUNTIME-05 WPA2、真实云端/音频、物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-24-user-firmware-six-device-matrix/followups/2026-10-25-refreshed-four-functional/followups/2026-10-25-sd-mbr-fixture/followups/2026-10-25-openai-nvs-precondition/) |
| 2026-10-25 | ESP Emulator | Worker-local StickS3 QEMU across network namespaces | PASS（virtual-device：18/18 checks、真实 QEMU、source/normalized firmware/QEMU SHA、serial/frame/QOM evidence、QEMU reap/namespace cleanup；physical cross-host/reattach/companion continuity/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-http-worker-executor/followups/2026-10-25-control-runtime-plane-split/followups/2026-10-25-worker-local-qemu/) |
| 2026-10-25 | ESP Emulator | ESP32-S3 WPA2-PSK 正确/错误密码数据面 | PASS（virtual-device：RSN/M1-M4/CCMP RX、正确密码 DHCP+DNS+TCP 443、错误密码 M2 MIC/deauth/无 DHCP、15/15 定向矩阵、377/377 tests + CI PASS；WPA3/group multicast/物理硬件 NOT RUN） | [查看](records/esp-emulator/2026-10-25-s3-wpa2-psk-data-plane/) |
| 2026-10-25 | ESP Emulator | 代码、文档与当前工作/待办收口 | PASS（docs/contracts：377/377、20/20、snapshot/catalog/coverage、CI PASS；当前状态/Backlog/工作流/代码地图/API/网络/runtime gap 同源；IPv4/IPv6 与 WPA2 稳定边界纠偏；真机与完整矩阵 NOT RUN） | [查看](records/esp-emulator/2026-10-25-code-doc-current-state-consolidation/) |
| 2026-10-25 | ESP Emulator | SHA-bound UI/headless/network-first 固件审查预期 | PASS（virtual-device：OpenAI BIN + isolated NVS 完成 guest marker、network PASS、DNS/TCP443、37-packet pcap；387/387、20/20、Node 与 CI PASS；真实 key/Realtime/RF/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-sha-bound-review-expectations/) |
| 2026-10-25 | ESP Emulator | HMAC-authenticated worker multicast discovery | PASS（virtual control-plane：worker 无硬编码 URL 注册、错误/旧 token reject、SIGHUP 后新 token 重新发现；391/391、20/20、Node 与 CI PASS；NAT/跨子网/跨主机/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-authenticated-worker-discovery/) |
| 2026-10-25 | ESP Emulator | Cross-subnet/NAT unicast worker discovery seed | PASS（virtual control-plane：两个 routed/masqueraded subnet、multicast 不跨 router、seed bootstrap、错误/旧 token reject、rotation、NAT source 和 cleanup，3/3×23 checks；442/442、29/29、Node 与两个 CI job PASS；物理跨主机/无 seed NAT/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-authenticated-worker-discovery/followups/2026-10-25-cross-subnet-nat-seed/) |
| 2026-10-25 | ESP Emulator | Worker central control-plane restart 与同 lease/evidence continuity | PASS（virtual-device：central 2.2s 重启、重注册、原 identity/generation/lease、terminal PASS、evidence ZIP、runtime/QEMU cleanup；393/393、20/20、Node 与 CI PASS；runtime restart/cross-host/claim dedup 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-worker-control-plane-restart-continuity/) |
| 2026-10-25 | ESP Emulator | Worker lease ownership fencing | PASS（control-plane/worker-local：re-claim 后旧 heartbeat/result 409、新 claim 完成；WorkerAgent 停止可达 runtime 且不报 stale result；433/433、27/27、Node/OpenAPI/Ruff/CI PASS；断网远端进程、外部 side effect、跨主机与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-worker-control-plane-restart-continuity/followups/2026-10-25-lease-ownership-fencing/) |
| 2026-10-25 | ESP Emulator | Worker network-partition side-effect fencing | PASS（virtual control-plane + worker-local QEMU/companion：bounded heartbeat、DELETE runtime、OS/QEMU PID reap、fresh retry、stale result suppress、lease expiry/requeue；process/QEMU 各 3/3×18，`qemu-unified` HTTP/BLE/pcap fence/retry 为 3/3×30；QEMU guest/device internal、worker 未拥有外部 side effect、物理跨主机与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-worker-control-plane-restart-continuity/followups/2026-10-25-lease-ownership-fencing/followups/2026-10-25-network-partition-side-effect-fencing/) |
| 2026-10-25 | ESP Emulator | Worker runtime-service restart 与 evidence continuity | PASS（virtual-device：runtime 2.2s 重启、同 session/PID、PID start-time/QMP reattach、worker evidence retry、原 job/lease PASS、session/QEMU cleanup；394/394、20/20、Node 与 CI PASS；create dedup/companion/cross-host/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-worker-runtime-service-restart/) |
| 2026-10-25 | ESP Emulator | Idempotent Device Service session creation | PASS（virtual-device：并发同 key 只建一个 session/QEMU、异请求 409、mapping SHA-only/0600、restart replay、worker response-loss retry；395/395、20/20、Node 与 CI PASS；跨主机/跨 tenant/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-session-create-idempotency/) |
| 2026-10-25 | ESP Emulator | 代码/文档总索引、自动规模快照与一页式交接 | PASS（docs/contracts：396/396、21/21、Node 2/2、catalog/profile/coverage/snapshot/compile/Ruff PASS；companion continuity、完整矩阵与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-code-doc-current-state-consolidation/followups/2026-10-25-code-doc-inventory-and-handoff/) |
| 2026-10-25 | ESP Emulator | 当前代码、文档新鲜度与待办重新校准 | PASS（docs/contracts：447/447、33/33、Node 2/2、文档职责/过期候选审计、Ruff E9/F 清理与两个 CI job PASS；完整功能矩阵、QEMU guest 内部 fence 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-code-doc-current-state-consolidation/followups/2026-10-25-work-doc-freshness-audit/) |
| 2026-10-25 | ESP Emulator | Secure Boot v2 image signature-sector evidence | PASS（static security：RSA-PSS、ECDSA P-256/P-384 block CRC/image digest、tampered/unsigned controls、13 checks；451/451、34/34、Node 与 CI PASS；signature math/eFuse trust/ROM execution/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-secure-boot-v2-image-evidence/) |
| 2026-10-25 | ESP Emulator | Secure Boot v2 RSA-PSS math verification | PASS（static security：block-embedded RSA public key、PSS/MGF1/SHA-256、valid + tampered signature controls、16 checks；452/452、34/34、Node 与 CI PASS；eFuse trust/ECDSA math/ROM/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-secure-boot-v2-image-evidence/followups/2026-10-25-rsa-pss-math-verification/) |
| 2026-10-25 | ESP Emulator | Trusted-host unified HTTP/BLE companion continuity | PASS（virtual-device：同 QEMU PID、HTTP generation 1→2、BLE peer adopt、重启后 GATT cycle 2 + guest HTTP recheck、原 job/lease evidence、26/26 checks；402/402、22/22、Node 与 CI PASS；namespace/Tab5/cross-host/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-worker-runtime-service-restart/followups/2026-10-25-unified-companion-continuity/) |
| 2026-10-25 | ESP Emulator | 有界 CIDR、controlled domain suffix 与代码/文档重整 | PASS（linux-virtual-network-policy：22/22 checks、411/411 tests、22/22 docs、Node/OpenAPI/Ruff/CI PASS；任意公网域名、guest domain lifecycle、跨主机与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-bounded-cidr-domain-policy/) |
| 2026-10-25 | ESP Emulator | Core2 active-stop、companion cleanup 与连续 session 恢复 | PASS（virtual-device：3/3 连续 session、BLE/HTTP active-stop、QEMU/BLE PID reap、worker lease release、下一 session 完整功能恢复；物理 cache/PSRAM、bit-exact controller、长时并发与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-core2-active-stop-recovery/) |
| 2026-10-25 | ESP Emulator | 镜像能力观察与 FirmwareManifest capability mismatch | PASS（static-manifest：公开 StickS3 Weather 观察 wifi/display、normal PASS、required camera 结构化拒绝；413/413 tests、22/22 docs、CI PASS；运行态、安全和真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-image-capability-observation/) |
| 2026-10-25 | ESP Emulator | WebBurner capability 来源、扫描覆盖与 warning 展示 | PASS（browser-ui：真实页面显示 SDKConfig/Image observations/Image scan、逐条 warning；Node/413 tests/CI PASS；无 QEMU、运行态与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-webburner-capability-display/) |
| 2026-10-25 | ESP Emulator | Core2 guest PSRAM 数据面与当前代码/文档重整 | PASS（virtual-device：3 个独立 lease 均从 4 MiB 虚拟堆分配 1 MiB 并完成三轮读回，同实例 WiFi/公网/NUS GATT/frame/QOM/pcap PASS；417 tests、23 docs、Node/CI PASS；物理 8 MiB/cache timing 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-code-doc-current-state-consolidation/followups/2026-10-25-core2-psram-doc-freshness/) |
| 2026-10-25 | ESP Emulator | Core2 持续 PSRAM 与周期联网压力 | PASS（virtual-device：3×120s、35/35/36 次 1 MiB 全缓冲校验、累计 106 MiB；30 次受控 HTTP、10 次公网 recheck；active BLE/HLI/pcap/cleanup PASS，418 tests + CI；物理 8 MiB/cache timing 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-code-doc-current-state-consolidation/followups/2026-10-25-core2-psram-doc-freshness/followups/2026-10-25-sustained-psram-network-stress/) |
| 2026-10-25 | ESP Emulator | Core2 600 秒 PSRAM、WiFi 与 active BLE soak | PASS（virtual-device：179 次 1 MiB 全缓冲校验、51 次受控 HTTP、18 次公网 recheck；active BLE/HLI/bounded TCG/912-packet pcap/cleanup PASS，20 个 RSS 采样 +352 KiB；物理 8 MiB/cache timing 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-code-doc-current-state-consolidation/followups/2026-10-25-core2-psram-doc-freshness/followups/2026-10-25-sustained-psram-network-stress/followups/2026-10-25-psram-600s-soak/) |
| 2026-10-25 | ESP Emulator | WebBurner 分段 size/SHA-256/SHA-1/MD5 完整性 | PASS（static-manifest：3/3 segments 复算并记录算法集合；SHA-256/size mismatch、非法 digest、冲突/未知 integrity 声明均拒绝；419 tests + CI；发布者签名、启动、安全执行与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-webburner-browser-intake/followups/2026-10-25-webburner-part-integrity/) |
| 2026-10-25 | ESP Emulator | 公网 Issue #1 复现与 macOS runtime bundle | PARTIAL（issue 基线失效和补丁冲突已复现；发布 71 MiB macOS arm64 runtime，clean clone 中 StickS3/Nesso 经 Device Service 取得 frame/input PASS；clean-room source rebuild、Linux/Windows 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-public-runtime-bundle-issue-1/) |
| 2026-10-25 | ESP Emulator | Bounded DNS CNAME、Device Service 策略与代码/文档重整 | PASS（resolver-data-plane：exact/domain terminal、chain encoding、8 跳边界、cycle/越权/冲突拒绝；425/425 tests、Node、OpenAPI、snapshot、Ruff 与 CI PASS；同 guest CNAME→TCP/HTTP、public DNS、RF 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-bounded-dns-cname-and-code-doc-reconciliation/) |
| 2026-10-25 | ESP Emulator | Firmware guest CNAME→HTTP lifecycle 与 `NET-07` closure | PASS（virtual-device：3 个独立 Device Service lease；guest CNAME→terminal A→HTTP 200、NXDOMAIN、denied port、DNS/HTTP/pcap/cleanup 同 bundle；427/427 tests + CI PASS；public DNS/DNSSEC、RF 与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-bounded-dns-cname-and-code-doc-reconciliation/followups/2026-10-25-cname-guest-lifecycle/) |
| 2026-10-25 | ESP Emulator | Worker-local QEMU across independent Docker containers | PASS（virtual-device：central/worker 分属两容器，跨 bridge terminal job、worker-local QEMU、三哈希 evidence、QEMU reap、container/bridge cleanup 均成立，3/3；428 tests + CI；物理跨主机/RF/真机 NOT RUN） | [查看](records/esp-emulator/2026-10-24-http-worker-executor/followups/2026-10-25-control-runtime-plane-split/followups/2026-10-25-worker-local-qemu/followups/2026-10-25-cross-container-qemu/) |
| 2026-10-25 | ESP Emulator | 工程交接总览、文档职责与新鲜度收敛 | PASS（docs/contracts：新增一页代码/工作/待办交接，统一入口并锁定全部 Backlog Task、动态计数和 UIFlow2 固定基线；429 tests、26 docs、Node/OpenAPI/snapshot/CI PASS；QEMU 功能与真机 NOT RUN） | [查看](records/esp-emulator/2026-10-25-code-doc-current-state-consolidation/followups/2026-10-25-engineering-handoff-and-freshness/) |
| 2026-10-24 | m5stack-schematics-text | AI Pyramid `llm-llm` deb 平台路径修正与全量链接审计 | PASS（链接/索引/下载哈希一致；100 个 deb 链接无 404、无其他平台错配；PR #2 OPEN/MERGEABLE，待管理员审核） | [查看](records/m5stack-schematics-text/2026-10-24-ai-pyramid-llm-deb-link/) |

## 目录结构

```text
agent-work-logs/
|-- records/<target>/<YYYY-MM-DD>-<topic>/       # 对外
|-- internal/records/<target>/<YYYY-MM-DD>-<topic>/  # 仅内网
|   |-- README.md  report.md  run.json
|   `-- evidence/  patches/  code/
|-- docs/
|-- templates/
`-- scripts/publish.sh
```

## 安全约束

- 公开层不得出现 token、密钥、内网 URL 或 IP、服务器路径、账号标识、设备唯一标识、客户数据。
- 默认不提交固件二进制、ELF 或 map 文件；记录 artifact 标识、大小和可重建工程即可。
- 不可逆操作（擦除、烧录、写标签、量产、OTA）必须在报告中写明风险与授权范围。
- 原始日志可裁剪噪声，但不得改写会影响结论的字节、错误码或时间顺序。

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

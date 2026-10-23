# ESP Emulator P0 网络、固件与 Core2 收口报告

## 背景

ESP Emulator 已具备多设备 QEMU、UIFlow2 外设矩阵、Device Service 和单 guest
unified runtime。本轮要补齐三个长期 P0：

1. 网络 namespace、DNS/egress policy、pcap、负向认证和断线重连；
2. Core2 cache/PSRAM 启动稳定性、原生无线、DNS 和公网访问；
3. 标准 FirmwareManifest、WebBurner 导入、安全配置和 capability mismatch。

原有文档和实现同时存在状态漂移：namespace/pcap 已开始实现但架构文仍写未实现，
Core2 曾被标为 cache panic，用户固件矩阵仍把它描述成已知启动 blocker，固件输入
也没有统一 manifest 和结构化能力拒绝。

## 结论

- 网络主路径现在以同一 QEMU guest 的 board + WiFi + HCI BLE 为准；Linux
  namespace runner 采用 fail-closed，无法创建 private namespace 时不会降级到
  宿主网络。
- Core2 最初的“cache panic”分类不准确。失败时两个 CPU 位于 idle `WAITI`，
  QEMU cache illegal-access callback 未进入；根因指向虚拟 timer/interrupt
  starvation。使用 `tcg,thread=single` 加 deterministic icount 后，10 次独立
  首轮运行全部 PASS。
- 固件入口现在支持 merged/segmented、M5Burner sidecar、WebBurner
  `manifest.json`、ESP-IDF `flasher_args.json`、ZIP 和 sparse image 规范化；
  SoC、Flash、PSRAM、安全状态和 capability mismatch 由 manifest/Device
  Service 结构化检查。
- 当前 P0 尚未全部关闭，因此总状态为 `PARTIAL`。

## 改动范围

### 网络

- 新增 `network_policy.py`：isolation、egress、DNS 和 pcap 策略；
- 新增 Linux `network_sandbox.py`：private namespace、无外部路由、
  namespace-local HTTP/BLE fixture 和 fail-closed 启动；
- 新增 `pcap_summary.py`：flow、DNS、DHCP、ARP、egress scope 和 payload hash；
- QEMU radio session 默认保留 pcap 和摘要；
- Device Service 新增 `POST /sessions/{id}/network-fault`，通过 QMP
  `wifi0` link down/up 验证 guest 重新 DHCP 和数据面恢复；
- `network_lane.py` 增加 incorrect-credential 负向 profile；
- `runtime=network` 明确拒绝 pcap，因为该后端没有 Ethernet capture 接口。

### Core2

- Core2 radio/unified 启动改用：

  ```text
  -accel tcg,thread=single
  -icount shift=auto,align=off,sleep=off
  ```

- 同一 `m5core2` guest 完成显示/触摸、AXP2101、INA3221、MPU6886、
  PCF8563、扬声器/麦克风、OpenMAC WiFi、公网 IPv4 DNS/HTTP 和 UART1
  HCI-offload BLE GATT；
- QOM 注入保持 guest 运行，不通过 QMP stop/continue 改变时序；
- 保留 `attempts` 作为诊断重试，但不把重试通过当成稳定性证据。

### 固件

- 新增版本化 `firmware_manifest.schema.json` 和 importer；
- ZIP 路径穿越、文件数、总解压大小、segment 重叠/越界和 artifact hash/size
  均有检查；
- sparse image 补齐到完整虚拟 Flash，分析 bootloader、partition table、
  app image 和 app descriptor；
- unknown secure boot / Flash Encryption 保持 `unknown`；
- Device Service 支持 `kind=manifest`，capability 缺口返回
  `409 unsupported_firmware_capability` 和结构化 `issues[]`；
- 使用三个公开固件样本完成 round-trip。

### 文档和代码组织

- 新增 `docs/code-map.md`，集中说明代码入口、运行时链路、验证入口、证据优先级
  和文档维护规则；
- `project-status` 只记录当前能力，`project-backlog` 只记录未完成项；
- 修正架构文、网络方案、Core2 调查、用户固件矩阵和部署文档中的旧口径；
- 增加文档旧结论和链接一致性测试。

## 执行环境

- 主干测试：macOS Apple Silicon，Python 3 和仓库 QEMU runtime；
- Linux namespace/QEMU：Linux arm64 容器；
- QEMU source commit：
  `M5StopWatch-QEMU@32d86576e783988fef1a489cb362dfda92a7aeda`；
- Linux `qemu-system-xtensa` SHA256：
  `22c84199187d47ebbe3bd66073583d2d8f042d60e974c4f4d9d549564cdb7290`。

## 验证结果

| 层级 | 状态 | 依据 |
| --- | --- | --- |
| build | PASS | `compileall`、OpenAPI/schema parse、`git diff --check` |
| flash | PASS | Device Service reference/uploaded flash 路径和 manifest session preflight |
| transport | PASS | QEMU NIC/DMA、DHCP/DNS/HTTP、UART1 HCI BLE、pcap |
| device_response | PASS | Core2 板级外设、WiFi、公网 HTTP、BLE GATT 和 frame/input |
| data_behavior | PASS | 错误认证拒绝、link down/up 后重新 DHCP、前后 HTTP、sparse 镜像补齐 |
| visual_or_physical | PASS | virtual-device 非黑帧和触摸重绘；物理显示未测 |
| review | PASS | `210/210` tests、`67/67` matrix、`274/274` checks |
| delivery | PASS | 源码提交和双远端 work-log 待本记录发布后确认 |

聚合证据：

- Linux namespace 65 个包，private namespace、无外部路由、DNS 查询无响应、
  pcap 无 global/SLiRP-redirect 目标；
- Core2 10/10 first-attempt PASS，Device Service `qemu-unified` 网络证据
  14 checks、受控公网 HTTP 200；
- FirmwareManifest 三个公开样本 PASS，StickS3 的 `camera` capability
  mismatch 被结构化拒绝；
- 平台测试 `210/210` PASS；full matrix `67/67/274` PASS。

## 风险和边界

- 本记录所有设备行为均为 virtual-device validation，不是物理硬件测量。
- QEMU WiFi 是 guest-visible MAC/DMA 加 user-net 数据面，不是完整 PHY/RF；
  WPA2/WPA3、天线、干扰、距离和功耗未证明。
- HCI-offload GATT 不是 Core2 原生 BT controller/radio；原生 controller
  外部 peer/GATT 仍为 `NOT RUN`。
- deterministic icount 只缓解当前虚拟 timer starvation，不等价于物理
  cache/PSRAM 时序。
- namespace runner 不是完整恶意固件沙箱；文件系统、资源隔离、allowlist、
  TLS 测试 CA 和正式 worker 生命周期仍待补。
- 三个 manifest 样本只证明格式和 preflight，不证明所有厂商固件兼容。

## 回滚

源码提交为单一增量 commit
`11bdf8fc3ed0588b4fb2ad7783d6b894489588fb`。回滚该 commit 可恢复之前状态，
但会同时撤销网络 sandbox/pcap、FirmwareManifest、Core2 确定性调度和文档收敛。
本轮没有擦除或修改物理设备，没有不可恢复的外部状态。

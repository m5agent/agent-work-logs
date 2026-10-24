# ESP Emulator P0 网络、Core2 与 FirmwareManifest 推进

- 日期：`2026-10-24`
- 结果：`PARTIAL`（三项 P0 新增可执行证据与 harness 修复；物理/controller/长期边界仍开放）
- 工作类型：`code_and_validation`
- 源码仓库：`m5agent/m5stack-esp-emulator`
- 源码版本：`e27a7c95ea2838fd2790ed10f0b95035025bf06a`
- 基线版本：`730123da116ece1acbd97744de419e97596f0232`
- CI：<https://github.com/m5agent/m5stack-esp-emulator/actions/runs/40063860563>
- 环境：macOS Apple Silicon；GitHub Actions Ubuntu；Python 3；Node.js；QEMU Core2；ESP-IDF 测试固件；公开 StickS3 固件

## 结论

- 网络错误密码新增独立 runner 和脱敏证据：6 次 auth/reject、无 DHCP、无 HTTP
  进度、固件 `no IP` 失败 marker 和 SoftAP wrong-password warning 同次
  `7/7 PASS`；
- DNS/UDP 数据面新增当前工作树证据：DNS 解析、host 收到固定 UDP 载荷、
  guest 收到同载荷回包 `5/5 PASS`；它不等于 controlled DNS policy；
- Core2 stock internal-controller 镜像通过 2 个独立 `/api/v1` lease，每个
  hold 120 秒，`2/2 PASS`。每轮同时通过 frame/QOM、WiFi、公网 DNS/HTTP、
  外部 NUS GATT、pcap、evidence 和 HLI health，且 `gdb_bridge=false`；
- 公开 StickS3 Weather 固件的 merged 与 WebBurner 三 segment 输入规范化到
  同一个 8 MiB artifact SHA256；camera-on-StickS3 返回结构化
  `unsupported_capability`；Manifest 19 项与定向 service/security 6 项测试
  PASS；
- 修复了 Core2 runner 的 QOM 截断和 peer-close 尾态分类：snapshot 上限从
  250 提高到 1000，只有 `peer-closed>0` 且 TX/RX queue 深度/丢包证据成立时
  才接受 `QUEUE_FULL`。

## 关键证据

- 平台套件：`299/299 PASS`，0 skipped；
- Node SHA256/upload client：`2/2 PASS`；
- runtime coverage、peripheral catalog、QEMU profiles、compileall、Ruff：
  全部 `PASS`；
- GitHub Actions `40063860563`：platform contracts 与 network namespace
  policy 均 `success`；
- Core2：`2×120s PASS`，每轮 48/48 HLI posts/consumed、39 events、
  9 ACLs、`hli-errors=0`、HLI/meta queue 为空；
- firmware：public sample manifest / WebBurner / capability mismatch 见下方
  evidence；
- 网络 wrong-password / DNS-UDP 见下方 evidence。

## 仍未闭合

- 物理 Core2 cache/PSRAM 时序等价性、bit-exact Espressif BT
  controller/baseband、同 guest 重复重连、WiFi/BLE coexistence 和多小时
  soak；
- 本次没有重跑 QEMU namespace+pcap reconnect 全链路；GitHub CI 重跑了
  namespace/egress policy，既有 QEMU pcap/reconnect evidence 仍引用历史记录；
- FirmwareManifest 不证明 boot、network、secure-boot 执行、eFuse 运行时状态
  或真机安全配置；
- 完整 UIFlow2 外设矩阵和物理硬件验证均 `NOT RUN`。

## 文件

- `report.md`：执行、根因、证据和边界；
- `run.json`：机器可读结果；
- `evidence/verification.summary.json`：本地与 CI 聚合；
- `evidence/p0-results.summary.json`：三个 P0 的压缩结果；
- `patches/`、`code/`：不适用，代码和完整 evidence 位于源码仓库。

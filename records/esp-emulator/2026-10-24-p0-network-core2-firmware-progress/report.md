# ESP Emulator P0 网络、Core2 与 FirmwareManifest 推进报告

## 背景

本轮目标是推进三项 P0：

1. network namespace、DNS/egress policy、pcap、错误密码、断线和重连；
2. Core2 cache/PSRAM 稳定性、原生 BT controller、DNS/公网访问；
3. 标准 FirmwareManifest、WebBurner 导入、安全配置和 capability mismatch。

仓库已有大量实现和历史 evidence，因此本轮不重复建模型，而是为当前代码补：

- 尚无独立入口的错误密码负向证据；
- DNS/UDP 当前工作树证据；
- 比现有 60 秒更长的 Core2 独立 lease；
- 同一公开固件的 merged / WebBurner / capability mismatch 交叉验证。

## 网络 P0

### 错误密码

新增 `tests/network/wrong_password/run_test.py`。runner 调用既有
`network_lane.py` 的 `esp-idf-wrong-password` profile，随后删除宿主路径和
command 中的密码，只保留 artifact role/size/SHA256、检查项、serial hash
和边界。

ESP32-S3 ESP-IDF HTTP 固件使用错误凭据加入 lab AP：

- 6 次 `wifi:state init -> auth`；
- 6 次 `auth -> init (0x600)`；
- 没有 DHCP lease；
- 没有 `HTTP_TPUT:` 进度；
- 固件最终输出 `HTTP_TPUT_RESULT: FAILED (no IP in 20s)`；
- SoftAP 记录 `wrong password on the station?`；
- `7/7` 负向检查 PASS。

### DNS/UDP

ESP-IDF fixture 完成 DHCP、DNS 解析、固定 UDP 载荷发送和带
`UDP_REPLY:` 前缀的同载荷回包。host peer、guest marker 和 evidence
三者一致，`5/5 PASS`。

该 DNS 走 host forwarder，证据中固定记录
`controlled_resolver=false`；它不是 Linux namespace 下的 A/NXDOMAIN
策略验证。namespace、exact IPv4 egress 和 nftables 失败关闭由同 commit
GitHub Actions `network-namespace-policy` job 重跑并通过。

## Core2 P0

### 正确输入

`core2-native-hci` 必须使用 stock internal-controller app：

```text
.work/uiflow-core2-2.5.3/m5stack/build-M5STACK_Core2
```

不能用 `build-M5STACK_Core2-hciuart3`。后者是 UART HCI-offload 镜像；错用后
public network 可以启动，但 NimBLE 会反复报 `HCI wait for ack returned 19`。
该错误已写入 runner README，避免再次误判。

### 2×120 秒 lease

使用当前 stock unified 镜像、匹配 ELF 和 patched QEMU，通过真实
`/api/v1` 创建 2 个独立 lease，每轮 hold 120 秒：

- firmware SHA256：`b9c91c40e60867186717938e075da8b19271cc8e7a22323524be213beff81982`；
- ELF SHA256：`5bec056bb775bcc94bc020e4fa411def097ea17b108dcd597d9cdab3c347db49`；
- QEMU SHA256：`667ec84c9e53ce73b0e63c7be69284837ff00b77a9194577ef757c164e8e31a1`；
- `2/2` 独立 lease PASS；
- 每轮 frame/QOM、WiFi DHCP/HTTP、公网 DNS/HTTP、NUS GATT、pcap、
  evidence ZIP 和 HLI health 全部 PASS；
- 每轮 48/48 HLI posts/consumed、39 C2H events、9 ACLs、`hli-errors=0`、
  HLI/meta queue 深度为 0；
- 两轮 frame SHA256 一致；
- `gdb_bridge=false`。

### runner 修复

前两次确认性运行暴露的是 harness 问题，不是 guest panic：

1. QOM snapshot 只请求 250 个字段，`tx-queue-depth` 在排序末尾被截断；
2. GATT peer 正常关闭后 guest 继续发送 HCI command，TX queue 达到 32，
   `last-error=2` 表示 `QUEUE_FULL`；
3. 旧 predicate 只接受 peer-close 后的 `WRITE` 尾态，因此把所有功能检查和
   120 秒 hold 都 PASS 的轮次误判为 HLI health FAIL。

修复：

- QOM snapshot `max_nodes` 250 -> 1000；
- 收集 `dropped-packets` 与 `tx-queue-depth`；
- 只在 `peer-closed>0` 且 TX queue 深度或 RX dropped packet 证据成立时接受
  `QUEUE_FULL`；
- HLI errors、HLI/meta queue depth 和非 peer-close queue-full 仍为 FAIL；
- 新增 `test_core2_native_hci_runner.py` 覆盖接受/拒绝路径。

### 边界

`2×120s` 是 virtual-device validation，证明当前 QEMU stock H2C/C2H、HLI、
WiFi/公网和外部 Bumble 路径可在两个独立 lease 中持续两分钟；它不证明：

- 物理 cache/PSRAM 时序；
- bit-exact Espressif BT controller/baseband；
- 同一 guest 内重复 GATT reconnect；
- WiFi/BLE 多小时 coexistence 或 RF。

## FirmwareManifest P0

公开样本：StickS3 Weather firmware ID `2108939572843147265`。

### merged 输入

- 原始 sparse image：8,323,072 bytes；
- normalized full flash：8,388,608 bytes；
- artifact SHA256：
  `d291e77f782399e37fd5b464f9b206a00654b2c10556d730d1c45667156c603f`；
- Manifest ID：
  `152451cbb9fedac361e0fe6341c56a4a945c1bac2bb7581d94dbaa437380e244`；
- status `PASS`。

### WebBurner 输入

同一镜像拆成 bootloader / partition-table / application 三个 part，并由
WebBurner `manifest.json` 导入：

- source format 被识别为 `web-manifest`；
- artifact kind 为 `segmented-flash`；
- 3 个非重叠 segment；
- normalized artifact SHA256 与 merged 输入一致；
- status `PASS`。

### capability mismatch

对 StickS3 声明 required capability `camera`：

- CLI/Manifest status `REJECTED`；
- issue code `unsupported_capability`；
- requirement `camera`；
- 列出 StickS3 可用的 audio/BLE/button/display/IMU/IR/microphone/PSRAM/
  speaker/WiFi；
- Device Service 定向契约同样返回 `unsupported_firmware_capability`，不创建
  session。

### 安全配置

`test_firmware_manifest.py` 全 19 项 PASS；定向 service/security 6 项 PASS。
覆盖 eFuse summary precedence、配置态/运行时声明分层、raw secret 不进入
manifest/output、summary 不复制、unverified warning，以及未建模 secure
boot/flash encryption 的拒绝。

这不等于真机 eFuse、生产 key、secure boot 执行或法律许可结论。

## 验证

```text
PYTHONPATH=platform/tools python3 -m unittest discover \
  -s platform/tests -p 'test_*.py'
Ran 299 tests in 9.864s
OK

runtime coverage  PASS
peripheral catalog PASS
QEMU profiles      PASS
compileall         PASS
Ruff               PASS
SHA256             PASS
FIRMWARE_UPLOAD    PASS
git diff --check   PASS
```

GitHub Actions `40063860563`：

- `platform-contracts`：success；
- `network-namespace-policy`：success。

## 验证边界

- 完整 UIFlow2 `67/67` 外设矩阵本轮未重跑；
- QEMU namespace+pcap reconnect 全链路本轮未重跑；CI 重跑 namespace/egress
  policy，历史 QEMU pcap/reconnect evidence 仍链接在源码文档；
- Core2 同 guest 重复重连、多小时 coexistence 和物理等价性 `NOT RUN`；
- FirmwareManifest 的 boot/network/secure-boot runtime `NOT RUN`；
- 物理硬件、RF、电气、功耗、声学、光学和机械验证 `NOT RUN`。

## 回滚

回滚源码提交 `e27a7c95ea2838fd2790ed10f0b95035025bf06a` 可移除新增 runner、
QOM/peer-close 分类修复、证据和文档更新；不会修改 QEMU build、固件二进制、
Device Service 历史或已有 evidence。本轮没有不可逆硬件操作。
